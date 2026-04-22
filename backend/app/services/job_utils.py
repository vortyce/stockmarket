import contextlib
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.job_log import JobLog

@contextlib.contextmanager
def job_logging(db: Session, job_name: str):
    """
    Context manager to automatically log job execution status.
    """
    log = JobLog(
        job_name=job_name,
        status="running",
        start_time=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    
    try:
        yield log
        log.status = "success"
    except Exception as e:
        log.status = "error"
        log.error_message = str(e)
        raise e
    finally:
        log.end_time = datetime.utcnow()
        db.commit()
