import uuid
from datetime import datetime, date
from sqlalchemy import String, Numeric, DateTime, ForeignKey, Date, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base


class TrendSnapshot(Base):
    __tablename__ = "trend_snapshots"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String, ForeignKey("companies.id"), index=True)
    as_of_date: Mapped[date] = mapped_column(Date, index=True)
    
    # Growth YoY
    revenue_yoy: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    ebit_yoy: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    net_income_yoy: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    
    # Margin & Debt Trends
    ebit_margin_current: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    ebit_margin_previous: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    margin_delta: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    
    net_debt_current: Mapped[float | None] = mapped_column(Numeric(20, 2), nullable=True)
    net_debt_previous: Mapped[float | None] = mapped_column(Numeric(20, 2), nullable=True)
    debt_delta: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    
    # Flags
    buyback_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    guidance_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    earnings_revision_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    improvement_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
