import uuid
from datetime import datetime, date
from sqlalchemy import String, Numeric, DateTime, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base


class RiskFlag(Base):
    __tablename__ = "risk_flags"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String, ForeignKey("companies.id"), index=True)
    as_of_date: Mapped[date] = mapped_column(Date, index=True)
    
    # Penalties (mostly 0 or positive values to be subtracted from score)
    non_recurring_profit_penalty: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    recurring_negative_fcf_penalty: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    debt_up_income_down_penalty: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    unsustainable_payout_penalty: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    margin_deterioration_penalty: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    governance_penalty: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    binary_event_penalty: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    accounting_penalty: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    
    total_penalty: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
