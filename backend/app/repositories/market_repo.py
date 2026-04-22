from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.models.market import MarketSnapshot


class MarketRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert_market_snapshot(self, data: dict):
        stmt = insert(MarketSnapshot).values(**data)
        stmt = stmt.on_conflict_do_update(
            index_elements=["company_id", "as_of_date"],
            set_={k: v for k, v in data.items() if k not in ["company_id", "as_of_date"]}
        )
        self.db.execute(stmt)
        self.db.commit()
    def get_latest_price_by_ticker(self, ticker: str) -> Optional[float]:
        from app.models.company import Company
        from sqlalchemy import select, desc
        
        stmt = select(MarketSnapshot.price).join(Company).where(
            Company.ticker == ticker
        ).order_by(desc(MarketSnapshot.as_of_date)).limit(1)
        
        return self.db.execute(stmt).scalar_one_or_none()
