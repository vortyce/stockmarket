import uuid
from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base

class PortfolioPosition(Base):
    """
    Foundation for Phase 6. Tracks user holdings for options suggestions.
    """
    __tablename__ = "portfolio_positions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ticker: Mapped[str] = mapped_column(String(20), index=True)
    company_id: Mapped[str | None] = mapped_column(String, ForeignKey("companies.id"), nullable=True)
    
    quantity: Mapped[float] = mapped_column(Numeric(20, 8), default=0.0)
    average_price: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    
    # New fields for Options Module
    is_core_position: Mapped[bool] = mapped_column(default=False)
    allow_covered_call: Mapped[bool] = mapped_column(default=True)
    thesis_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PortfolioCash(Base):
    """
    Tracks available balance for Cash-Secured Put suggestions.
    """
    __tablename__ = "portfolio_cash"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    amount: Mapped[float] = mapped_column(Numeric(20, 2), default=0.0)
    currency: Mapped[str] = mapped_column(String(10), default="BRL")
    
    # New field for Options Module
    reserved_cash: Mapped[float] = mapped_column(Numeric(20, 2), default=0.0)
    
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
