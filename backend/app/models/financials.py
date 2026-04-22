import uuid
from datetime import datetime
from sqlalchemy import String, Numeric, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base


class FinancialsAnnual(Base):
    __tablename__ = "financials_annual"
    __table_args__ = (UniqueConstraint("company_id", "year", name="uq_financials_annual_company_year"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String, ForeignKey("companies.id"), index=True)
    year: Mapped[int] = mapped_column(Integer)
    
    # Values
    revenue: Mapped[float | None] = mapped_column(Numeric(20, 2), nullable=True)
    ebit: Mapped[float | None] = mapped_column(Numeric(20, 2), nullable=True)
    ebitda: Mapped[float | None] = mapped_column(Numeric(20, 2), nullable=True)
    net_income: Mapped[float | None] = mapped_column(Numeric(20, 2), nullable=True)
    cfo: Mapped[float | None] = mapped_column(Numeric(20, 2), nullable=True)
    fcf: Mapped[float | None] = mapped_column(Numeric(20, 2), nullable=True)
    dividends: Mapped[float | None] = mapped_column(Numeric(20, 2), nullable=True)
    equity: Mapped[float | None] = mapped_column(Numeric(20, 2), nullable=True)
    net_debt: Mapped[float | None] = mapped_column(Numeric(20, 2), nullable=True)
    
    # Calculated Metrics
    ebit_margin: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    net_margin: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    roe: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    roic: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    payout: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    eps: Mapped[float | None] = mapped_column(Numeric(20, 4), nullable=True)
    bvps: Mapped[float | None] = mapped_column(Numeric(20, 4), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
