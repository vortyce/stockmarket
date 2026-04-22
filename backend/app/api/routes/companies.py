from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.company_repo import CompanyRepository
from app.schemas.company import CompanyOut

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[CompanyOut])
def list_companies(sector: str | None = Query(default=None), db: Session = Depends(get_db)):
    repo = CompanyRepository(db)
    return repo.list_companies(sector=sector)


@router.get("/{ticker}", response_model=CompanyOut)
def get_company(ticker: str, db: Session = Depends(get_db)):
    repo = CompanyRepository(db)
    company = repo.get_by_ticker(ticker)
    if not company:
        raise HTTPException(status_code=404, detail="Ticker não encontrado")
    return company

@router.get("/{ticker}/financials")
def get_company_financials(ticker: str, db: Session = Depends(get_db)):
    from app.models.financials import FinancialsAnnual
    repo = CompanyRepository(db)
    company = repo.get_by_ticker(ticker)
    if not company:
        raise HTTPException(status_code=404, detail="Ticker não encontrado")
    
    financials = db.query(FinancialsAnnual).filter(FinancialsAnnual.company_id == company.id).order_by(FinancialsAnnual.year.desc()).all()
    return financials

@router.get("/{ticker}/market")
def get_company_market(ticker: str, db: Session = Depends(get_db)):
    from app.models.market import MarketSnapshot
    repo = CompanyRepository(db)
    company = repo.get_by_ticker(ticker)
    if not company:
        raise HTTPException(status_code=404, detail="Ticker não encontrado")
        
    market = db.query(MarketSnapshot).filter(MarketSnapshot.company_id == company.id).order_by(MarketSnapshot.as_of_date.desc()).first()
    return market
