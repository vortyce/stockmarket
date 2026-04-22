import uuid
from datetime import datetime, date
from sqlalchemy import String, Numeric, DateTime, ForeignKey, Date, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base


class RankingSnapshot(Base):
    __tablename__ = "ranking_snapshots"
    __table_args__ = (UniqueConstraint("company_id", "as_of_date", "scope", name="uq_ranking_snapshots_company_date_scope"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String, ForeignKey("companies.id"), index=True)
    as_of_date: Mapped[date] = mapped_column(Date, index=True)
    model_version: Mapped[str] = mapped_column(String(20), default="v1.0.0", index=True)
    
    scope: Mapped[str] = mapped_column(String(50), default="general") # general, sector, bucket
    position: Mapped[int] = mapped_column(Integer)
    
    # Redundancy for easy access
    final_score: Mapped[float] = mapped_column(Numeric(10, 2))
    bucket: Mapped[str | None] = mapped_column(String(100), nullable=True)
    rating_class: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
