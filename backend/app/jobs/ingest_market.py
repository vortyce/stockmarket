from app.db.session import SessionLocal
from app.models.company import Company
from app.providers.yahoo import YahooMarketProvider
from app.repositories.market_repo import MarketRepository
from app.core.logging import setup_logging
import logging
from datetime import date

setup_logging()
logger = logging.getLogger("jobs.ingest_market")

def run_ingest_market():
    db = SessionLocal()
    try:
        companies = db.query(Company).filter(Company.is_active == True).all()
        if not companies:
            logger.warning("No active companies found for market ingestion.")
            return

        provider = YahooMarketProvider()
        repo = MarketRepository(db)
        
        today = date.today()
        
        for company in companies:
            logger.info(f"Fetching market data for {company.ticker}...")
            quote = provider.get_quote(company.ticker)
            
            if quote:
                market_data = {
                    "company_id": company.id,
                    "as_of_date": today,
                    "price": quote.price,
                    "pe": quote.pe,
                    "pb": quote.pb,
                    "dividend_yield": quote.dividend_yield,
                    "ev_ebitda": quote.ev_ebitda,
                    "market_cap": quote.market_cap,
                    "enterprise_value": quote.enterprise_value
                }
                repo.upsert_market_snapshot(market_data)
                logger.info(f"Market data updated for {company.ticker}")
            else:
                logger.warning(f"Could not update market data for {company.ticker}")
                
    except Exception as e:
        logger.error(f"Critical error in market ingestion: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_ingest_market()
