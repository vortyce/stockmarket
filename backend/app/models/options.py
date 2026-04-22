import uuid
from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Float, Integer, Date, DateTime, ForeignKey, Text, JSON, UniqueConstraint, Boolean, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

class OptionChainSnapshot(Base):
    __tablename__ = "option_chain_snapshots"
    __table_args__ = (
        UniqueConstraint("ticker", "option_symbol", "snapshot_date", name="uq_option_snapshot_daily"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ticker: Mapped[str] = mapped_column(String(20), index=True)
    option_symbol: Mapped[str] = mapped_column(String(20), index=True)
    option_type: Mapped[str] = mapped_column(String(10))  # CALL / PUT
    
    expiration_date: Mapped[date] = mapped_column(Date, index=True)
    dte: Mapped[int] = mapped_column(Integer)
    strike: Mapped[float] = mapped_column(Float)
    
    # Prices
    bid: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ask: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mid_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Volume and Liquidity
    volume: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    open_interest: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Symbols tracking
    option_symbol_raw: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    option_display_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Greeks and IV
    implied_volatility: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    delta: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    theta: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    gamma: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    vega: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    underlying_price: Mapped[float] = mapped_column(Float)
    snapshot_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    snapshot_date: Mapped[date] = mapped_column(Date, default=lambda: datetime.utcnow().date(), index=True)

class OptionsPolicyConfig(Base):
    __tablename__ = "options_policy_configs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    policy_name: Mapped[str] = mapped_column(String(50), unique=True)
    
    # DTE Range
    min_dte: Mapped[int] = mapped_column(Integer, default=30)
    max_dte: Mapped[int] = mapped_column(Integer, default=45)
    exit_dte: Mapped[int] = mapped_column(Integer, default=21)
    
    # Profit Target
    profit_target_pct: Mapped[float] = mapped_column(Float, default=0.50)
    
    # Delta Ranges
    covered_call_delta_min: Mapped[float] = mapped_column(Float, default=0.15)
    covered_call_delta_max: Mapped[float] = mapped_column(Float, default=0.25)
    cash_put_delta_min: Mapped[float] = mapped_column(Float, default=0.15)
    cash_put_delta_max: Mapped[float] = mapped_column(Float, default=0.25)
    
    # Liquidity Filters
    min_open_interest: Mapped[int] = mapped_column(Integer, default=300)
    min_bid: Mapped[float] = mapped_column(Float, default=0.15)
    max_spread_pct: Mapped[float] = mapped_column(Float, default=0.20)
    
    # Rule Flags
    allow_calls_on_deep_value: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_puts_on_rerating: Mapped[bool] = mapped_column(Boolean, default=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class OptionSuggestion(Base):
    __tablename__ = "options_suggestions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ticker: Mapped[str] = mapped_column(String(20), index=True)
    suggestion_type: Mapped[str] = mapped_column(String(20)) # COVERED_CALL / CASH_SECURED_PUT
    
    option_symbol: Mapped[str] = mapped_column(String(20))
    strike: Mapped[float] = mapped_column(Float)
    expiration_date: Mapped[date] = mapped_column(Date)
    
    premium: Mapped[float] = mapped_column(Float) # Expected premium (mid or bid)
    delta: Mapped[float] = mapped_column(Float)
    
    # Symbols tracking
    option_symbol_raw: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    option_display_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    contracts: Mapped[int] = mapped_column(Integer)
    capital_required: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    effective_entry_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    overlay_score: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="PENDING") # PENDING, ACCEPTED, IGNORED, EXPIRED
    
    reason_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    risk_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

class OptionPosition(Base):
    __tablename__ = "options_positions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_ticker: Mapped[str] = mapped_column(String(20), index=True)
    option_symbol: Mapped[str] = mapped_column(String(20), index=True)
    option_type: Mapped[str] = mapped_column(String(10))
    
    contracts: Mapped[int] = mapped_column(Integer)
    strike: Mapped[float] = mapped_column(Float)
    expiration_date: Mapped[date] = mapped_column(Date)
    
    entry_price: Mapped[float] = mapped_column(Float)
    entry_date: Mapped[date] = mapped_column(Date)
    
    status: Mapped[str] = mapped_column(String(20), default="OPEN") # OPEN, CLOSED, EXERCISED, ROLLED
    
    # Exit conditions (at the moment of entry)
    exit_target_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    exit_dte_rule: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    profit_target_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    close_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    result_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class OptionRollAction(Base):
    __tablename__ = "options_roll_actions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    original_position_id: Mapped[str] = mapped_column(String, ForeignKey("options_positions.id"))
    new_position_id: Mapped[str] = mapped_column(String, ForeignKey("options_positions.id"))
    
    roll_date: Mapped[date] = mapped_column(Date, default=date.today)
    net_credit_debit: Mapped[float] = mapped_column(Float)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
