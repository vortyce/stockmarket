from pydantic import BaseModel, ConfigDict
from datetime import date


class ScoreOut(BaseModel):
    ticker: str
    company_name: str
    as_of_date: date
    sector: str | None = None
    
    # Raw scores
    quality_raw: float
    valuation_raw: float
    dividends_raw: float
    trend_raw: float
    gov_liq_raw: float
    
    # Weighted scores
    quality_weighted: float
    valuation_weighted: float
    dividends_weighted: float
    trend_weighted: float
    gov_liq_weighted: float
    
    penalty: float
    final_score: float
    rating_class: str | None = None
    bucket: str | None = None
    summary: str | None = None

    model_config = ConfigDict(from_attributes=True)
