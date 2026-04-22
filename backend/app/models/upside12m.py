import uuid
from datetime import date, datetime
from sqlalchemy import Column, String, Float, Integer, Date, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class ResearchTarget(Base):
    __tablename__ = "research_targets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("companies.id"), nullable=False, index=True)
    target_price = Column(Float, nullable=False)
    source_name = Column(String, nullable=False)
    rating_recommendation = Column(String, nullable=False) # e.g. "Buy", "Neutral", "Sell"
    current_price_snapshot = Column(Float, nullable=False) # Price of the stock when target was captured
    source_url = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    as_of_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    company = relationship("Company")


class Upside12MSnapshot(Base):
    __tablename__ = "upside_12m_snapshots"
    __table_args__ = (
        UniqueConstraint("company_id", "as_of_date", name="uq_upside12m_snapshot"),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("companies.id"), nullable=False, index=True)
    as_of_date = Column(Date, nullable=False, index=True)
    
    # Raw Blocks
    upside_ext_raw = Column(Float, nullable=False, default=0.0)
    rerating_raw = Column(Float, nullable=False, default=0.0)
    recup_operacional_raw = Column(Float, nullable=False, default=0.0)
    assimetria_raw = Column(Float, nullable=False, default=0.0)
    gov_liq_raw = Column(Float, nullable=False, default=0.0)
    penalties_raw = Column(Float, nullable=False, default=0.0)
    
    # Final outputs
    final_score = Column(Float, nullable=False)
    bucket = Column(String, nullable=False)
    rating_class = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    
    # Audit
    model_version = Column(String, nullable=False, server_default="v1.0")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    company = relationship("Company")


class Upside12MRanking(Base):
    __tablename__ = "upside_12m_rankings"
    __table_args__ = (
        UniqueConstraint("company_id", "as_of_date", name="uq_upside12m_ranking_company_date"),
        UniqueConstraint("position", "as_of_date", name="uq_upside12m_ranking_position_date")
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    as_of_date = Column(Date, nullable=False, index=True)
    position = Column(Integer, nullable=False)
    
    # Denormalized fields to avoid JOINs
    company_id = Column(String, ForeignKey("companies.id"), nullable=False, index=True)
    score_snapshot_id = Column(String, ForeignKey("upside_12m_snapshots.id"), nullable=False)
    final_score = Column(Float, nullable=False)
    bucket = Column(String, nullable=False)
    rating_class = Column(String, nullable=False)
    
    # Audit
    model_version = Column(String, nullable=False, server_default="v1.0")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    company = relationship("Company")
    snapshot = relationship("Upside12MSnapshot")
