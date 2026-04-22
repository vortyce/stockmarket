import uuid
from datetime import datetime
from sqlalchemy import String, Numeric, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base


class SectorConfig(Base):
    __tablename__ = "sector_configs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sector: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    
    # Weights (0.0 to 1.0)
    weight_quality: Mapped[float] = mapped_column(Numeric(5, 2), default=0.20)
    weight_valuation: Mapped[float] = mapped_column(Numeric(5, 2), default=0.20)
    weight_dividends: Mapped[float] = mapped_column(Numeric(5, 2), default=0.20)
    weight_trend: Mapped[float] = mapped_column(Numeric(5, 2), default=0.20)
    weight_gov_liq: Mapped[float] = mapped_column(Numeric(5, 2), default=0.20)
    
    # Specific sector rules
    use_debt_ebitda: Mapped[bool] = mapped_column(default=True)
    use_pb_strong: Mapped[bool] = mapped_column(default=False)
    use_dividend_strong: Mapped[bool] = mapped_column(default=False)
    
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
