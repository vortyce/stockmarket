from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.models.financials import FinancialsAnnual


class FinancialsRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert_financials(self, data: dict):
        stmt = insert(FinancialsAnnual).values(**data)
        stmt = stmt.on_conflict_do_update(
            index_elements=["company_id", "year"],
            set_={k: v for k, v in data.items() if k not in ["company_id", "year"]}
        )
        self.db.execute(stmt)
        self.db.commit()

    def get_by_company_year(self, company_id: str, year: int):
        stmt = select(FinancialsAnnual).where(
            FinancialsAnnual.company_id == company_id,
            FinancialsAnnual.year == year
        )
        return self.db.execute(stmt).scalar_one_or_none()
