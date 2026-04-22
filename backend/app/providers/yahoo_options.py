import logging
from typing import List
import yfinance as yf
from app.providers.base_options import OptionsDataProvider, OptionQuote

logger = logging.getLogger(__name__)

class YahooOptionsProvider(OptionsDataProvider):
    """
    EXPERIMENTAL Fallback provider using yfinance. 
    Note: Currently, yfinance has very limited or no support for B3 (Brazilian) option chains.
    """
    
    def get_provider_name(self) -> str:
        return "YahooFinance (Experimental)"

    def get_option_chain(self, ticker: str) -> List[OptionQuote]:
        logger.info(f"Attempting to fetch option chain from Yahoo Finance for {ticker}")
        
        # yfinance expects .SA for Brazilian stocks
        yf_ticker = f"{ticker}.SA" if not ticker.endswith(".SA") else ticker
        
        try:
            # Note: ticker.options usually returns () for B3 stocks
            stock = yf.Ticker(yf_ticker)
            expirations = stock.options
            
            if not expirations:
                logger.warning(f"No option chain found for {ticker} on Yahoo Finance. yfinance support for B3 options is limited.")
                return []
                
            # If data were available, we would iterate through expirations and fetch calls/puts
            # For now, we return empty to avoid breaking the pipeline with incomplete data.
            return []
            
        except Exception as e:
            logger.error(f"Error fetching option chain from Yahoo for {ticker}: {e}")
            return []
