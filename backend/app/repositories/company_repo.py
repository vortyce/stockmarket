from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.company import Company


class CompanyRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_companies(self, sector: str | None = None):
        stmt = select(Company).order_by(Company.ticker)
        if sector:
            stmt = stmt.where(Company.sector == sector)
        return self.db.execute(stmt).scalars().all()

    def get_by_ticker(self, ticker: str):
        stmt = select(Company).where(Company.ticker == ticker.upper())
        return self.db.execute(stmt).scalar_one_or_none()

    def upsert_company(self, data: dict):
        from sqlalchemy.dialects.postgresql import insert
        
        stmt = insert(Company).values(**data)
        stmt = stmt.on_conflict_do_update(
            index_elements=["ticker"],
            set_={k: v for k, v in data.items() if k != "ticker"}
        )
        self.db.execute(stmt)
        self.db.commit()
