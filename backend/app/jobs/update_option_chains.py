import logging
import time
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.options_chain_service import OptionsChainService
from app.repositories.portfolio_repo import PortfolioRepository
from app.repositories.upside12m_repo import Upside12MRepository
from app.db import base # noqa
from app.models.job_log import JobLog
from app.db import base # noqa

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("update_option_chains")

def run_update_option_chains():
    """
    Background job to refresh option chains for relevant tickers:
    - Stocks in user portfolio
    - Stocks in Upside 12M Top 20 ranking
    """
    db = SessionLocal()
    start_time = datetime.utcnow()
    job_log = JobLog(
        job_name="update_option_chains",
        status="RUNNING",
        start_time=start_time,
        records_processed=0
    )
    db.add(job_log)
    db.commit()
    
    try:
        service = OptionsChainService(db)
        portfolio_repo = PortfolioRepository(db)
        upside_repo = Upside12MRepository(db)
        
        # 1. Collect tickers from portfolio
        portfolio_tickers = {p.ticker for p in portfolio_repo.get_positions()}
        
        # 2. Collect tickers from Upside 12M Top 20
        ranking = upside_repo.get_latest_ranking()
        ranking_tickers = {r.company.ticker for r in ranking}
        
        # Merge all unique tickers
        all_tickers = portfolio_tickers.union(ranking_tickers)
        logger.info(f"Starting option chain update for {len(all_tickers)} tickers")
        
        total_options = 0
        for ticker in all_tickers:
            try:
                count = service.update_ticker_chain(ticker)
                total_options += count
                # Avoid hitting rate limits if too many tickers
                if len(all_tickers) > 5:
                    time.sleep(1) 
            except Exception as e:
                logger.error(f"Failed to update chain for {ticker}: {e}")
                continue
        
        job_log.status = "SUCCESS"
        job_log.end_time = datetime.utcnow()
        job_log.records_processed = total_options
        db.commit()
        logger.info(f"Job finished successfully. Total options processed: {total_options}")
        
    except Exception as e:
        logger.error(f"Critical failure in update_option_chains job: {e}")
        job_log.status = "FAILED"
        job_log.error_message = str(e)
        job_log.end_time = datetime.utcnow()
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    from datetime import datetime
    run_update_option_chains()
