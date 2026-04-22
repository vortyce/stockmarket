from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.models.upside12m import Upside12MRanking, Upside12MSnapshot
from app.models.company import Company
from app.repositories.upside12m_repo import Upside12MRepository

router = APIRouter(prefix="/upside12m", tags=["upside12m"])

@router.get("/top20")
def get_top20_upside(db: Session = Depends(get_db)):
    repo = Upside12MRepository(db)
    rankings = repo.get_latest_ranking()
    
    # Return as dict with joined company info
    result = []
    for r in rankings:
        result.append({
            "ticker": r.company.ticker,
            "company_name": r.company.company_name,
            "sector": r.company.sector,
            "position": r.position,
            "final_score": r.final_score,
            "bucket": r.bucket,
            "rating_class": r.rating_class,
            "as_of_date": r.as_of_date,
            "model_version": r.model_version
        })
    return result

@router.get("/{ticker}")
def get_upside_detail(ticker: str, db: Session = Depends(get_db)):
    repo = Upside12MRepository(db)
    
    # 1. find company
    comp = db.query(Company).filter(Company.ticker == ticker).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Ticker não encontrado")
        
    snap = repo.get_latest_snapshot(comp.id)
    if not snap:
        raise HTTPException(status_code=404, detail="Sem dados Upside 12M para esta empresa")
        
    target = repo.get_research_target(comp.id)
    
    return {
        "final_score": snap.final_score,
        "bucket": snap.bucket,
        "rating_class": snap.rating_class,
        "summary": snap.summary,
        "as_of_date": snap.as_of_date,
        "model_version": snap.model_version,
        "metrics": {
            "upside_ext_raw": snap.upside_ext_raw,
            "rerating_raw": snap.rerating_raw,
            "recup_operacional_raw": snap.recup_operacional_raw,
            "assimetria_raw": snap.assimetria_raw,
            "gov_liq_raw": snap.gov_liq_raw,
            "penalties_raw": snap.penalties_raw
        },
        "research_target": {
            "target_price": target.target_price if target else None,
            "current_price_snapshot": target.current_price_snapshot if target else None,
            "source_name": target.source_name if target else None,
            "rating_recommendation": target.rating_recommendation if target else None
        }
    }

@router.get("/history")
def get_upside_history(ticker: str = Query(...), limit: int = 12, db: Session = Depends(get_db)):
    comp = db.query(Company).filter(Company.ticker == ticker).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Ticker não encontrado")
        
    stmt = select(Upside12MSnapshot).where(
        Upside12MSnapshot.company_id == comp.id
    ).order_by(Upside12MSnapshot.as_of_date.desc()).limit(limit)
    
    snaps = db.execute(stmt).scalars().all()
    
    return [{
        "as_of_date": s.as_of_date,
        "final_score": s.final_score,
        "bucket": s.bucket
    } for s in snaps]

@router.post("/jobs/recalculate")
def trigger_recalculate():
    import threading
    from app.jobs.recalculate_upside12m import run_upside12m_recalculation
    t = threading.Thread(target=run_upside12m_recalculation)
    t.start()
    return {"message": "Job Upside 12M_Recalculation disparado em background"}
