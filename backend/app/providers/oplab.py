import requests
import os
import logging
from typing import List, Optional
from datetime import datetime, date
from app.providers.base_options import OptionsDataProvider, OptionQuote

logger = logging.getLogger(__name__)

class OplabOptionsProvider(OptionsDataProvider):
    def __init__(self):
        self.base_url = os.getenv("OPLAB_API_BASE_URL", "https://api.oplab.com.br/v3").rstrip("/")
        self.token = os.getenv("OPLAB_API_TOKEN")
        self.headers = {
            "Access-Token": self.token,
            "Content-Type": "application/json"
        }

    def get_provider_name(self) -> str:
        return "OpLab"

    def get_option_chain(self, ticker: str) -> List[OptionQuote]:
        if not self.token:
            logger.error("OpLab API Token not configured")
            return []

        # OpLab endpoint for options: /market/options/{symbol}
        # Note: Ticker in Brazil usually PETR4, Oplab might expect PETR4
        url = f"{self.base_url}/market/options/{ticker}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # Oplab usually returns a flat list of all options for the underlying
            # but sometimes it's a dict with 'options' key and 'underlying_price'
            if isinstance(data, dict):
                options_list = data.get("options", [])
                underlying_price = data.get("underlying_price") or data.get("close") or 0.0
            else:
                options_list = data
                # If it's a list, we'll try to get spot_price from the first option item later
                underlying_price = 0.0
            
            quotes = []
            for i, opt in enumerate(options_list):
                try:
                    # Map real OpLab fields
                    curr_symbol = opt.get("symbol")
                    if i < 2: # Log first 2 items per ticker to avoid log flooding
                        logger.info(f"Oplab Raw Option: symbol={curr_symbol}, name={opt.get('name')}, due={opt.get('due_date')}")
                        
                    quotes.append(OptionQuote(
                        ticker=ticker,
                        option_symbol=curr_symbol,
                        option_type=opt.get("category", opt.get("type", "")).upper(), 
                        expiration_date=datetime.strptime(opt.get("due_date"), "%Y-%m-%d").date(),
                        dte=opt.get("days_to_maturity", 0),
                        strike=float(opt.get("strike", 0)),
                        bid=opt.get("bid"),
                        ask=opt.get("ask"),
                        last=opt.get("close"), # 'close' is used as 'last' in OpLab list
                        mid_price=opt.get("mid") or ((opt.get("bid", 0) + opt.get("ask", 0)) / 2 if opt.get("bid") and opt.get("ask") else None),
                        volume=opt.get("volume"),
                        open_interest=opt.get("open_interest"),
                        implied_volatility=opt.get("iv"), # Usually None in mass list
                        delta=opt.get("delta"), # Usually None in mass list
                        theta=opt.get("theta"),
                        gamma=opt.get("gamma"),
                        vega=opt.get("vega"),
                        underlying_price=opt.get("spot_price") or underlying_price,
                        snapshot_at=datetime.utcnow(),
                        snapshot_date=datetime.utcnow().date(),
                        option_symbol_raw=curr_symbol,
                        option_display_code=curr_symbol # OpLab doesn't have a separate tiny code in API
                    ))
                except Exception as e:
                    logger.warning(f"Error parsing option {opt.get('symbol')} for {ticker}: {e}")
                    continue
                    
            return quotes
            
        except Exception as e:
            logger.error(f"Error fetching option chain from OpLab for {ticker}: {e}")
            return []
