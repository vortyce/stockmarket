import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ticker: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    company_name: Mapped[str] = mapped_column(String(255))
    cnpj: Mapped[str | None] = mapped_column(String(32), nullable=True)
    cvm_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    sector: Mapped[str | None] = mapped_column(String(100), nullable=True)
    subsector: Mapped[str | None] = mapped_column(String(100), nullable=True)
    listing_segment: Mapped[str | None] = mapped_column(String(100), nullable=True)
    main_index: Mapped[str | None] = mapped_column(String(50), nullable=True)
    free_float: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    avg_daily_liquidity: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
