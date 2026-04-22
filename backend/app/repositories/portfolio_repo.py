from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from app.models.portfolio import PortfolioPosition, PortfolioCash
from typing import List, Optional

class PortfolioRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_positions(self) -> List[PortfolioPosition]:
        return self.db.execute(select(PortfolioPosition)).scalars().all()

    def get_position_by_id(self, pos_id: str) -> Optional[PortfolioPosition]:
        return self.db.get(PortfolioPosition, pos_id)

    def get_position_by_ticker(self, ticker: str) -> Optional[PortfolioPosition]:
        return self.db.execute(
            select(PortfolioPosition).where(PortfolioPosition.ticker == ticker)
        ).scalar_one_or_none()

    def save_position(self, pos: PortfolioPosition) -> PortfolioPosition:
        self.db.add(pos)
        self.db.commit()
        self.db.refresh(pos)
        return pos

    def delete_position(self, pos_id: str) -> bool:
        pos = self.get_position_by_id(pos_id)
        if pos:
            self.db.delete(pos)
            self.db.commit()
            return True
        return False

    def get_cash(self) -> PortfolioCash:
        cash = self.db.execute(select(PortfolioCash)).scalar_one_or_none()
        if not cash:
            # Initialize if not exists
            cash = PortfolioCash(amount=0.0, reserved_cash=0.0)
            self.db.add(cash)
            self.db.commit()
            self.db.refresh(cash)
        return cash

    def update_cash(self, amount: float, reserved_cash: Optional[float] = None) -> PortfolioCash:
        cash = self.get_cash()
        cash.amount = amount
        if reserved_cash is not None:
            cash.reserved_cash = reserved_cash
        self.db.commit()
        self.db.refresh(cash)
        return cash
