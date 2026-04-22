from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.options_chain_service import OptionsChainService
from app.services.options_policy_service import OptionsPolicyService
from app.repositories.options_repo import OptionsRepository
from app.services.options_monitoring_service import OptionsMonitoringService
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

router = APIRouter(prefix="/options", tags=["options"])

class PolicyUpdate(BaseModel):
    min_dte: Optional[int] = None
    max_dte: Optional[int] = None
    exit_dte: Optional[int] = None
    profit_target_pct: Optional[float] = None
    covered_call_delta_min: Optional[float] = None
    covered_call_delta_max: Optional[float] = None
    cash_put_delta_min: Optional[float] = None
    cash_put_delta_max: Optional[float] = None
    min_open_interest: Optional[int] = None
    min_bid: Optional[float] = None
    max_spread_pct: Optional[float] = None

@router.get("/chains/{ticker}")
def get_option_chain(ticker: str, db: Session = Depends(get_db)):
    service = OptionsChainService(db)
    chain = service.get_latest_chain(ticker)
    if not chain:
        # Try to trigger a fetch if no data exists
        service.update_ticker_chain(ticker)
        chain = service.get_latest_chain(ticker)
    
    return {
        "ticker": ticker,
        "snapshot_at": chain[0].snapshot_at if chain else None,
        "items": chain
    }

@router.get("/policy")
def get_policy(db: Session = Depends(get_db)):
    service = OptionsPolicyService(db)
    return service.get_current_policy()

@router.patch("/policy")
def update_policy(data: PolicyUpdate, db: Session = Depends(get_db)):
    service = OptionsPolicyService(db)
    updates = data.dict(exclude_unset=True)
    return service.update_policy(updates)

@router.get("/suggestions")
def get_all_suggestions(db: Session = Depends(get_db)):
    repo = OptionsRepository(db)
    sugs = repo.get_suggestions()
    
    # Calculate DTE on the fly
    today = date.today()
    result = []
    for s in sugs:
        d = s.__dict__.copy()
        if "_sa_instance_state" in d: del d["_sa_instance_state"]
        d["dte"] = (s.expiration_date - today).days
        result.append(d)
    return result

@router.get("/suggestions/covered-calls")
def get_covered_calls(db: Session = Depends(get_db)):
    repo = OptionsRepository(db)
    sugs = repo.get_suggestions(suggestion_type="COVERED_CALL")
    
    today = date.today()
    result = []
    for s in sugs:
        d = s.__dict__.copy()
        if "_sa_instance_state" in d: del d["_sa_instance_state"]
        d["dte"] = (s.expiration_date - today).days
        result.append(d)
    return result

@router.get("/suggestions/cash-puts")
def get_cash_put_suggestions(db: Session = Depends(get_db)):
    repo = OptionsRepository(db)
    sugs = repo.get_suggestions(suggestion_type="CASH_PUT")
    
    today = date.today()
    result = []
    for s in sugs:
        d = s.__dict__.copy()
        if "_sa_instance_state" in d: del d["_sa_instance_state"]
        d["dte"] = (s.expiration_date - today).days
        result.append(d)
    return result

@router.post("/suggestions/{suggestion_id}/accept")
def accept_suggestion(suggestion_id: str, custom_shares: Optional[int] = None, db: Session = Depends(get_db)):
    repo = OptionsRepository(db)
    pos = repo.accept_suggestion(suggestion_id, custom_shares)
    if not pos:
        raise HTTPException(status_code=404, detail="Suggestion not found or already accepted")
    return {"message": "Suggestion accepted and position created", "position_id": pos.id}

# Monitoring and Rolling
@router.get("/positions")
def get_options_positions(db: Session = Depends(get_db)):
    repo = OptionsRepository(db)
    return repo.get_open_positions()

@router.get("/monitor")
def get_options_monitor(db: Session = Depends(get_db)):
    service = OptionsMonitoringService(db)
    return service.get_monitored_positions()

@router.get("/roll-suggestions")
def get_roll_suggestions(db: Session = Depends(get_db)):
    service = OptionsMonitoringService(db)
    return service.get_roll_suggestions()

@router.post("/jobs/monitor-exits")
def trigger_monitor_exits():
    import threading
    from app.jobs.monitor_option_exits import run_monitor_option_exits
    t = threading.Thread(target=run_monitor_option_exits)
    t.start()
    return {"status": "queued", "job": "monitor_option_exits"}

@router.post("/jobs/update-option-chains")
def trigger_update_options_job():
    import threading
    from app.jobs.update_option_chains import run_update_option_chains
    t = threading.Thread(target=run_update_option_chains)
    t.start()
    return {"status": "queued", "job": "update_option_chains"}

@router.post("/jobs/generate-options-suggestions")
def trigger_generate_suggestions_job():
    import threading
    from app.jobs.generate_options_suggestions import run_generate_options_suggestions
    t = threading.Thread(target=run_generate_options_suggestions)
    t.start()
    return {"status": "queued", "job": "generate_options_suggestions"}
