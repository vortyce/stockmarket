import logging
from datetime import datetime
from app.db.session import SessionLocal
from app.services.options_suggestion_service import OptionsSuggestionService
from app.db import base # noqa
from app.models.job_log import JobLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("generate_options_suggestions")

def run_generate_options_suggestions():
    """
    Background job to process option chains and identify 
    CC and CSP opportunities.
    """
    db = SessionLocal()
    start_time = datetime.utcnow()
    job_log = JobLog(
        job_name="generate_options_suggestions",
        status="RUNNING",
        start_time=start_time,
        records_processed=0
    )
    db.add(job_log)
    db.commit()
    
    try:
        service = OptionsSuggestionService(db)
        logger.info("Starting options suggestion generation...")
        
        service.generate_all_suggestions()
        
        # Count total suggestions created
        from app.models.options import OptionSuggestion
        from sqlalchemy import func, select
        cc_count = db.execute(select(func.count()).select_from(OptionSuggestion).where(OptionSuggestion.status == "ACTIVE", OptionSuggestion.suggestion_type == "COVERED_CALL")).scalar()
        csp_count = db.execute(select(func.count()).select_from(OptionSuggestion).where(OptionSuggestion.status == "ACTIVE", OptionSuggestion.suggestion_type == "CASH_PUT")).scalar()
        total = cc_count + csp_count
        
        job_log.status = "SUCCESS"
        job_log.end_time = datetime.utcnow()
        job_log.records_processed = total
        db.commit()
        logger.info(f"Job finished successfully. Total: {total} (CC: {cc_count}, CSP: {csp_count})")
        
    except Exception as e:
        logger.error(f"Critical failure in generate_options_suggestions job: {e}")
        job_log.status = "FAILED"
        job_log.error_message = str(e)
        job_log.end_time = datetime.utcnow()
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    run_generate_options_suggestions()
