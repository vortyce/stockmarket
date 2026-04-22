import logging
from app.db.session import SessionLocal
from app.services.b3_service import B3Service
from app.services.cvm_service import CVMService
from app.services.b3_service import B3Service # Actually we already have it
from app.services.scoring_service import ScoringService
from app.services.ranking_service import RankingService
from app.models.company import Company
from app.services.job_utils import job_logging
from app.core.logging import setup_logging
import yfinance as yf
from datetime import datetime

setup_logging()
logger = logging.getLogger("jobs.full_refresh")

def run_full_refresh():
    db = SessionLocal()
    
    # We use a single outer log for the full refresh or individual logs for each step?
    # User said "registrar no job_logs e interromper o pipeline".
    # I'll create a main log entry.
    
    with job_logging(db, "full_refresh") as main_log:
        try:
            # 1. Ingest B3
            logger.info("Step 1/4: Ingesting B3 Companies...")
            b3_service = B3Service(db)
            b3_stats = b3_service.ingest_companies()
            main_log.records_processed += b3_stats.get("inserted", 0) + b3_stats.get("updated", 0)
            
            # 2. Ingest CVM (Financials)
            logger.info("Step 2/4: Ingesting CVM Financials (2022-2023)...")
            cvm_service = CVMService(db)
            cvm_stats = cvm_service.ingest_annual_data(years=[2022, 2023])
            main_log.records_processed += cvm_stats.get("processed", 0)
            
            # 3. Ingest Market Data
            logger.info("Step 3/4: Ingesting Market Data...")
            from app.providers.yahoo import YahooMarketProvider
            from app.repositories.market_repo import MarketRepository
            from datetime import date
            
            provider = YahooMarketProvider()
            market_repo = MarketRepository(db)
            companies = db.query(Company).filter(Company.is_active == True).all()
            
            for comp in companies:
                try:
                    quote = provider.get_quote(comp.ticker)
                    
                    # Update free float natively here using yfinance if it's missing (0.0)
                    import yfinance as yf
                    yf_ticker = f"{comp.ticker}.SA" if not comp.ticker.endswith(".SA") else comp.ticker
                    stock_info = yf.Ticker(yf_ticker).info
                    shares = stock_info.get("sharesOutstanding")
                    float_shares = stock_info.get("floatShares")
                    
                    if shares and float_shares and shares > 0:
                        calculated_float = float_shares / shares
                        # Basic cap since Brazil yfinance float is sometimes > 1 for PN shares
                        if 0 < calculated_float <= 1.0:
                            comp.free_float = calculated_float
                        elif calculated_float > 1.0:
                            comp.free_float = 0.99  # Fallback approximation for corrupted PN data
                    
                    if quote:
                        # Fix 2: Normalize dividend_yield
                        # Yahoo Finance sometimes returns DY as a whole number (e.g. 15.59)
                        # instead of a decimal (0.1559). Anything > 1.0 must be divided by 100.
                        raw_dy = quote.dividend_yield
                        if raw_dy and raw_dy > 1.0:
                            raw_dy = raw_dy / 100.0

                        market_data = {
                            "company_id": comp.id,
                            "as_of_date": date.today(),
                            "price": quote.price,
                            "pe": quote.pe,
                            "pb": quote.pb,
                            "dividend_yield": raw_dy,
                            "ev_ebitda": quote.ev_ebitda,
                            "market_cap": quote.market_cap,
                            "enterprise_value": quote.enterprise_value
                        }
                        market_repo.upsert_market_snapshot(market_data)
                        main_log.records_processed += 1
                except Exception as e:
                    logger.warning(f"Error for {comp.ticker}: {e}")
                    continue
            
            db.commit() # Commit the new free_float updates
            
            # 4. Recalculate Scores & Rankings
            logger.info("Step 4/4: Recalculating Scores and Rankings...")
            scoring_service = ScoringService(db)
            for comp in companies:
                scoring_service.calculate_and_save(comp.ticker)
            
            ranking_service = RankingService(db)
            ranking_service.generate_top_rankings()
            
            logger.info("Full Refresh completed successfully.")
            
        except Exception as e:
            logger.error(f"Full Refresh failed at some step: {e}")
            raise e # job_logging will capture this

    db.close()

if __name__ == "__main__":
    run_full_refresh()
