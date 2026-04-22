from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.score import ScoreSnapshot
from app.models.company import Company


class ScoreRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_latest_by_ticker(self, ticker: str):
        stmt = (
            select(
                Company.ticker,
                Company.company_name,
                ScoreSnapshot
            )
            .join(Company, Company.id == ScoreSnapshot.company_id)
            .where(Company.ticker == ticker.upper())
            .order_by(ScoreSnapshot.as_of_date.desc())
            .limit(1)
        )
        result = self.db.execute(stmt).first()
        if not result:
            return None
        
        # Merge ticker and company_name into the ScoreSnapshot object attributes 
        # or return a combined dict that matches the schema
        ticker_val, name_val, score_obj = result
        
        # We can dynamically add attributes to the object for Pydantic to pick them up
        # since Pydantic uses from_attributes=True
        score_obj.ticker = ticker_val
        score_obj.company_name = name_val
        
        return score_obj

    def upsert_score_snapshot(self, data: dict):
        from sqlalchemy.dialects.postgresql import insert
        stmt = insert(ScoreSnapshot).values(**data)
        stmt = stmt.on_conflict_do_update(
            index_elements=["company_id", "as_of_date"],
            set_={
                c.name: stmt.excluded[c.name]
                for c in ScoreSnapshot.__table__.columns
                if c.name not in ["id", "company_id", "as_of_date", "created_at"]
            }
        )
        self.db.execute(stmt)
        self.db.commit()
