import uuid
from datetime import datetime, date
from sqlalchemy import String, Numeric, DateTime, ForeignKey, Date, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base


class ScoreSnapshot(Base):
    __tablename__ = "score_snapshots"
    __table_args__ = (UniqueConstraint("company_id", "as_of_date", name="uq_score_snapshots_company_date"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String, ForeignKey("companies.id"), index=True)
    as_of_date: Mapped[date] = mapped_column(Date, index=True)
    model_version: Mapped[str] = mapped_column(String(20), default="v1.0.0", index=True)
    
    # Raw scores (0-100 or specific ranges)
    quality_raw: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    valuation_raw: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    dividends_raw: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    trend_raw: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    gov_liq_raw: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    
    # Weighted scores
    quality_weighted: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    valuation_weighted: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    dividends_weighted: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    trend_weighted: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    gov_liq_weighted: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    
    # Final result
    penalty: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    final_score: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    
    rating_class: Mapped[str | None] = mapped_column(String(50), nullable=True) # Ex: Compra, Monitorar, Value Trap
    bucket: Mapped[str | None] = mapped_column(String(100), nullable=True) # Ex: Deep Value, Rerating
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
