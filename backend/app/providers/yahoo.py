import yfinance as yf
from typing import Dict, List, Optional
import logging
from app.providers.base import MarketProvider, MarketQuote

logger = logging.getLogger(__name__)

class YahooMarketProvider(MarketProvider):
    """
    PROVISIONAL Yahoo Finance Provider.
    This implementation uses the yfinance library and is intended for MVP purposes.
    """
    
    def get_quote(self, ticker: str) -> Optional[MarketQuote]:
        # yfinance expects .SA for Brazilian stocks
        yf_ticker = f"{ticker}.SA" if not ticker.endswith(".SA") else ticker
        
        try:
            stock = yf.Ticker(yf_ticker)
            info = stock.info
            
            if not info or "regularMarketPrice" not in info and "currentPrice" not in info:
                logger.warning(f"No market data found for {ticker} on Yahoo Finance")
                return None
            
            return MarketQuote(
                ticker=ticker,
                price=info.get("currentPrice") or info.get("regularMarketPrice"),
                pe=info.get("forwardPE") or info.get("trailingPE"),
                pb=info.get("priceToBook"),
                dividend_yield=info.get("dividendYield"),
                ev_ebitda=info.get("enterpriseToEbitda"),
                market_cap=info.get("marketCap"),
                enterprise_value=info.get("enterpriseValue"),
                fcf_yield=None # Yahoo doesn't provide FCF yield directly, would need calculation
            )
        except Exception as e:
            logger.error(f"Error fetching data from Yahoo for {ticker}: {e}")
            return None

    def get_quotes(self, tickers: List[str]) -> Dict[str, MarketQuote]:
        results = {}
        for ticker in tickers:
            quote = self.get_quote(ticker)
            if quote:
                results[ticker] = quote
        return results
