from app.db.session import SessionLocal
from app.models.company import Company
from app.services.scoring_service import ScoringService
from app.services.ranking_service import RankingService
from app.core.logging import setup_logging
import logging

setup_logging()
logger = logging.getLogger("jobs.recalculate_scores")

def run_recalculate_scores():
    db = SessionLocal()
    try:
        # 1. Scoring
        companies = db.query(Company).filter(Company.is_active == True).all()
        if not companies:
            logger.warning("No active companies found for scoring.")
            return

        scoring_service = ScoringService(db)
        for company in companies:
            try:
                scoring_service.calculate_and_save(company.ticker)
            except Exception as e:
                db.rollback() # Fix transactional state
                logger.error(f"Error scoring {company.ticker}: {e}")
        
        # 2. Ranking
        ranking_service = RankingService(db)
        ranking_service.generate_top_rankings()
        
        logger.info("Recalculate scores and rankings job completed successfully.")
                
    except Exception as e:
        logger.error(f"Critical error in recalculate_scores job: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_recalculate_scores()
