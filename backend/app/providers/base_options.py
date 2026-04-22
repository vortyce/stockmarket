from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, datetime

class OptionQuote(BaseModel):
    ticker: str
    option_symbol: str
    option_type: str  # CALL / PUT
    expiration_date: date
    dte: int
    strike: float
    
    bid: Optional[float] = None
    ask: Optional[float] = None
    last: Optional[float] = None
    mid_price: Optional[float] = None
    
    volume: Optional[int] = None
    open_interest: Optional[int] = None
    
    implied_volatility: Optional[float] = None
    delta: Optional[float] = None
    theta: Optional[float] = None
    gamma: Optional[float] = None
    vega: Optional[float] = None
    
    underlying_price: float
    option_symbol_raw: Optional[str] = None
    option_display_code: Optional[str] = None
    snapshot_at: datetime = datetime.utcnow()

class OptionsDataProvider(ABC):
    @abstractmethod
    def get_option_chain(self, ticker: str) -> List[OptionQuote]:
        """Fetches the full option chain for a given ticker."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Returns the name of the provider."""
        pass
