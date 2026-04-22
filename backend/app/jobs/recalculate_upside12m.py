import logging
import sys
from datetime import date
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.company import Company
from app.models.market import MarketSnapshot
from app.repositories.upside12m_repo import Upside12MRepository
from app.services.upside12m_scoring import Upside12MScoringService
from app.services.upside12m_ranking_service import Upside12MRankingService

logger = logging.getLogger(__name__)

def seed_targets_for_testing(db: Session, repo: Upside12MRepository):
    """Seeds some research targets for top tickers to demonstrate the ranking."""
    today = date.today()
    # Let's pick some major tickers we know are in the DB
    top_tickers = ['PETR4', 'VALE3', 'BBAS3', 'ITUB4', 'WEGE3', 'B3SA3', 'RENT3', 'SUZB3', 'ABEV3', 'LREN3']
    
    companies = db.query(Company).filter(Company.ticker.in_(top_tickers)).all()
    
    for comp in companies:
        # Get current price from latest snapshot
        mkt = db.query(MarketSnapshot).filter(
            MarketSnapshot.company_id == comp.id
        ).order_by(MarketSnapshot.as_of_date.desc()).first()
        
        if not mkt: continue
        
        price = float(mkt.price)
        # Mocking a target price with 20-50% upside
        upside_factor = 1.2 + (0.3 * (comp.id[0] > '8')) # pseudo-random but stable
        
        repo.upsert_research_target({
            "company_id": comp.id,
            "target_price": price * upside_factor,
            "source_name": "Goldman Sachs" if comp.ticker == 'PETR4' else "Itaú BBA",
            "rating_recommendation": "Buy",
            "current_price_snapshot": price,
            "source_url": "https://analise.exemplo.com/relatorio",
            "notes": "Relatório de cobertura anual - Foco em recuperação.",
            "as_of_date": today
        })
    db.commit()

def run_upside12m_recalculation():
    logger.info("--- Starting Upside 12M Recalculation Job ---")
    
    db: Session = SessionLocal()
    try:
        repo = Upside12MRepository(db)
        scoring = Upside12MScoringService(db)
        ranking_svc = Upside12MRankingService(db)
        
        today = date.today()
        
        # 1. Setup Test Data
        seed_targets_for_testing(db, repo)
        
        # 2. Score all companies
        companies = db.query(Company).all()
        logger.info(f"Processing {len(companies)} companies...")
        
        for comp in companies:
            try:
                score_data = scoring.calculate_score(comp, today)
                repo.upsert_snapshot(score_data)
            except Exception as e:
                logger.error(f"Error scoring {comp.ticker}: {e}")
                
        db.commit()
        
        # 3. Build the Ranking photography for today
        logger.info("Generating Top 20 Ranking...")
        ranking_svc.generate_ranking(today, limit=20)
        
        logger.info("--- Upside 12M Recalculation Job Finished ---")
        
    except Exception as e:
        logger.error(f"Job failed: {e}")
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    run_upside12m_recalculation()
