import logging
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.upside12m import Upside12MSnapshot
from app.repositories.upside12m_repo import Upside12MRepository

logger = logging.getLogger(__name__)

class Upside12MRankingService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = Upside12MRepository(db)

    def generate_ranking(self, as_of_date: date, limit: int = 20):
        """
        Generates the Top N ranking for Upside 12M based on the snapshots of a given date.
        Persists the result in the Upside12MRanking table.
        """
        # Get all snapshots for the given date, ordered by final_score desc
        stmt = select(Upside12MSnapshot).where(
            Upside12MSnapshot.as_of_date == as_of_date,
            Upside12MSnapshot.final_score > 0
        ).order_by(Upside12MSnapshot.final_score.desc()).limit(limit)
        
        top_snapshots = self.db.execute(stmt).scalars().all()
        
        if not top_snapshots:
            logger.warning(f"No snapshots found for {as_of_date}. Cannot generate ranking 12M.")
            return

        rankings_data = []
        for position, snap in enumerate(top_snapshots, start=1):
            rankings_data.append({
                "as_of_date": as_of_date,
                "position": position,
                "company_id": snap.company_id,
                "score_snapshot_id": snap.id,
                "final_score": snap.final_score,
                "bucket": snap.bucket,
                "rating_class": snap.rating_class,
                "model_version": snap.model_version
            })

        # Save to DB
        self.repo.save_ranking_batch(rankings_data)
        self.db.commit()
        
        logger.info(f"Upside 12M Ranking generated successfully with {len(rankings_data)} companies.")
        return rankings_data
