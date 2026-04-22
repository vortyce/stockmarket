from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from pydantic import BaseModel


class MarketQuote(BaseModel):
    ticker: str
    price: Optional[float] = None
    pe: Optional[float] = None
    pb: Optional[float] = None
    dividend_yield: Optional[float] = None
    ev_ebitda: Optional[float] = None
    market_cap: Optional[float] = None
    enterprise_value: Optional[float] = None
    fcf_yield: Optional[float] = None


class MarketProvider(ABC):
    @abstractmethod
    def get_quote(self, ticker: str) -> Optional[MarketQuote]:
        """Fetches market data for a single ticker."""
        pass

    @abstractmethod
    def get_quotes(self, tickers: List[str]) -> Dict[str, MarketQuote]:
        """Fetches market data for multiple tickers."""
        pass
