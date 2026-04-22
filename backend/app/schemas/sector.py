from pydantic import BaseModel, ConfigDict


class SectorConfigOut(BaseModel):
    id: str
    sector: str
    weight_quality: float
    weight_valuation: float
    weight_dividends: float
    weight_trend: float
    weight_gov_liq: float
    use_debt_ebitda: bool
    use_pb_strong: bool
    use_dividend_strong: bool
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)
