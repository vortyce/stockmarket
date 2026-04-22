from app.db.session import SessionLocal
from app.services.b3_service import B3Service
from app.core.logging import setup_logging
import logging

setup_logging()
logger = logging.getLogger("jobs.ingest_b3")

def run_ingest_b3():
    db = SessionLocal()
    try:
        service = B3Service(db)
        stats = service.ingest_companies()
        logger.info(f"B3 Ingestion completed. Stats: {stats}")
    except Exception as e:
        logger.error(f"Critical error in B3 ingestion: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_ingest_b3()
