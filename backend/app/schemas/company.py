from pydantic import BaseModel


class CompanyOut(BaseModel):
    id: str
    ticker: str
    company_name: str
    cnpj: str | None = None
    cvm_code: str | None = None
    sector: str | None = None
    subsector: str | None = None
    listing_segment: str | None = None
    main_index: str | None = None
    free_float: float | None = None
    avg_daily_liquidity: float | None = None

    class Config:
        from_attributes = True
