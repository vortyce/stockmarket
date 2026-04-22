from pydantic import BaseModel, ConfigDict
from datetime import date


class RankingOut(BaseModel):
    position: int
    ticker: str
    company_name: str | None = None
    sector: str | None = None
    final_score: float
    bucket: str | None = None
    rating_class: str | None = None
    as_of_date: date | None = None
    model_version: str | None = None

    model_config = ConfigDict(from_attributes=True)
