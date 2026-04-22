from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import date
import logging
from app.models.score import ScoreSnapshot
from app.models.ranking import RankingSnapshot
from app.repositories.ranking_repo import RankingRepository

logger = logging.getLogger(__name__)

class RankingService:
    def __init__(self, db: Session):
        self.db = db
        self.ranking_repo = RankingRepository(db)

    def generate_top_rankings(self):
        logger.info("Generating top rankings...")
        
        # 1. Fetch latest scores for all companies
        from sqlalchemy import func
        latest_scores_sub = self.db.query(
            ScoreSnapshot.company_id,
            func.max(ScoreSnapshot.as_of_date).label("latest_date")
        ).group_by(ScoreSnapshot.company_id).subquery()
        
        scores = self.db.query(ScoreSnapshot).join(
            latest_scores_sub,
            (ScoreSnapshot.company_id == latest_scores_sub.c.company_id) &
            (ScoreSnapshot.as_of_date == latest_scores_sub.c.latest_date)
        ).order_by(desc(ScoreSnapshot.final_score)).all()
        
        if not scores:
            logger.warning("No scores found to generate ranking.")
            return

        # 2. Persist to RankingSnapshot
        today = date.today()
        
        for i, score in enumerate(scores):
            ranking_data = {
                "company_id": score.company_id,
                "as_of_date": today,
                "model_version": "v1.0.0",
                "position": i + 1,
                "final_score": score.final_score,
                "bucket": score.bucket,
                "rating_class": score.rating_class,
                "scope": "general"
            }
            # Note: We need an upsert_ranking_snapshot in ranking_repo
            self.ranking_repo.upsert_ranking_snapshot(ranking_data)
            
        logger.info(f"Ranking generated with {len(scores)} companies.")
        return len(scores)
