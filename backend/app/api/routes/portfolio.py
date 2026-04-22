from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.portfolio_repo import PortfolioRepository
from app.models.portfolio import PortfolioPosition
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

class PositionCreate(BaseModel):
    ticker: str
    quantity: float
    average_price: float
    is_core_position: bool = False
    allow_covered_call: bool = True
    thesis_type: Optional[str] = None

class PositionUpdate(BaseModel):
    quantity: Optional[float] = None
    average_price: Optional[float] = None
    is_core_position: Optional[bool] = None
    allow_covered_call: Optional[bool] = None
    thesis_type: Optional[str] = None

class CashUpdate(BaseModel):
    available_cash: float
    reserved_cash_for_puts: Optional[float] = None

@router.get("/")
def get_portfolio(db: Session = Depends(get_db)):
    repo = PortfolioRepository(db)
    positions = repo.get_positions()
    return positions

@router.post("/positions")
def create_position(data: PositionCreate, db: Session = Depends(get_db)):
    repo = PortfolioRepository(db)
    pos = PortfolioPosition(
        ticker=data.ticker,
        quantity=data.quantity,
        average_price=data.average_price,
        is_core_position=data.is_core_position,
        allow_covered_call=data.allow_covered_call,
        thesis_type=data.thesis_type
    )
    repo.save_position(pos)
    return {"status": "created", "id": pos.id}

@router.patch("/positions/{id}")
def update_position(id: str, data: PositionUpdate, db: Session = Depends(get_db)):
    repo = PortfolioRepository(db)
    pos = repo.get_position_by_id(id)
    if not pos:
        raise HTTPException(status_code=404, detail="Posição não encontrada")
    
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(pos, key, value)
    
    db.commit()
    db.refresh(pos)
    return pos

@router.get("/cash")
def get_cash(db: Session = Depends(get_db)):
    repo = PortfolioRepository(db)
    cash = repo.get_cash()
    return {
        "available_cash": cash.amount,
        "reserved_cash_for_puts": cash.reserved_cash
    }

@router.patch("/cash")
def update_cash(data: CashUpdate, db: Session = Depends(get_db)):
    repo = PortfolioRepository(db)
    cash = repo.update_cash(data.available_cash, data.reserved_cash_for_puts)
    return {
        "available_cash": cash.amount,
        "reserved_cash_for_puts": cash.reserved_cash
    }
