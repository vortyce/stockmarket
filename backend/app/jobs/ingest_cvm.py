from app.db.session import SessionLocal
from app.services.cvm_service import CVMService
from app.core.logging import setup_logging
import logging
import argparse

setup_logging()
logger = logging.getLogger("jobs.ingest_cvm")

def run_ingest_cvm(years):
    db = SessionLocal()
    try:
        service = CVMService(db)
        for year in years:
            stats = service.download_and_parse_dfp(year)
            logger.info(f"CVM Ingestion for {year} completed. Stats: {stats}")
    except Exception as e:
        logger.error(f"Critical error in CVM ingestion: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--years", nargs="+", type=int, default=[2023, 2024])
    args = parser.parse_args()
    
    run_ingest_cvm(args.years)
