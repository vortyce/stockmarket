from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.ranking import RankingSnapshot
from app.models.company import Company
from datetime import date


class RankingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_top_rankings(
        self, 
        scope: str = "general", 
        as_of_date: date | None = None, 
        limit: int = 20
    ):
        stmt = (
            select(
                RankingSnapshot.position,
                RankingSnapshot.final_score,
                RankingSnapshot.bucket,
                RankingSnapshot.rating_class,
                RankingSnapshot.as_of_date,
                RankingSnapshot.model_version,
                Company.ticker,
                Company.company_name,
                Company.sector
            )
            .join(Company, Company.id == RankingSnapshot.company_id)
            .where(RankingSnapshot.scope == scope)
        )
        
        if as_of_date:
            stmt = stmt.where(RankingSnapshot.as_of_date == as_of_date)
        else:
            # If no date provided, we might want the latest available date for that scope
            # For the MVP, we can just get the most recent entries
            latest_date_stmt = select(RankingSnapshot.as_of_date).where(RankingSnapshot.scope == scope).order_by(RankingSnapshot.as_of_date.desc()).limit(1)
            latest_date = self.db.execute(latest_date_stmt).scalar()
            if latest_date:
                stmt = stmt.where(RankingSnapshot.as_of_date == latest_date)

        stmt = stmt.order_by(RankingSnapshot.position).limit(limit)
        
        results = self.db.execute(stmt).all()
        
        # Convert to list of dicts or objects compatible with RankingOut
        return [
            {
                "position": r.position,
                "ticker": r.ticker,
                "company_name": r.company_name,
                "sector": r.sector,
                "final_score": float(r.final_score),
                "bucket": r.bucket,
                "rating_class": r.rating_class,
                "as_of_date": r.as_of_date,
                "model_version": r.model_version
            }
            for r in results
        ]

    def upsert_ranking_snapshot(self, data: dict):
        from sqlalchemy.dialects.postgresql import insert
        stmt = insert(RankingSnapshot).values(**data)
        stmt = stmt.on_conflict_do_update(
            index_elements=["company_id", "as_of_date", "scope"],
            set_={
                c.name: stmt.excluded[c.name]
                for c in RankingSnapshot.__table__.columns
                if c.name not in ["id", "company_id", "as_of_date", "scope", "created_at"]
            }
        )
        self.db.execute(stmt)
        self.db.commit()
