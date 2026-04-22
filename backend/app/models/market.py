import uuid
from datetime import datetime, date
from sqlalchemy import String, Numeric, DateTime, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base


class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"
    __table_args__ = (UniqueConstraint("company_id", "as_of_date", name="uq_market_snapshots_company_date"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String, ForeignKey("companies.id"), index=True)
    as_of_date: Mapped[date] = mapped_column(Date, index=True)
    
    # Prices & Multiples
    price: Mapped[float | None] = mapped_column(Numeric(20, 2), nullable=True)
    pe: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    pb: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    ev_ebitda: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    fcf_yield: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    dividend_yield: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    
    # Absolute Valuations
    market_cap: Mapped[float | None] = mapped_column(Numeric(20, 2), nullable=True)
    enterprise_value: Mapped[float | None] = mapped_column(Numeric(20, 2), nullable=True)
    
    # Historical Context (5Y Averages)
    pe_5y_avg: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    pb_5y_avg: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    ev_ebitda_5y_avg: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    
    # Sector Context
    sector_pe_avg: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    sector_pb_avg: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    sector_ev_ebitda_avg: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    
    # Valuation Targets
    graham_number: Mapped[float | None] = mapped_column(Numeric(20, 2), nullable=True)
    graham_discount: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    simple_fair_value: Mapped[float | None] = mapped_column(Numeric(20, 2), nullable=True)
    fair_value_discount: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
