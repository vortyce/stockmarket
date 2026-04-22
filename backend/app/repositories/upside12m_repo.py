from datetime import date
from typing import List, Optional
from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
import logging

from app.models.upside12m import Upside12MSnapshot, Upside12MRanking, ResearchTarget

logger = logging.getLogger(__name__)

class Upside12MRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert_snapshot(self, snapshot_data: dict) -> Upside12MSnapshot:
        """
        Inserts or updates an Upside12MSnapshot.
        UniqueConstraint(company_id, as_of_date) ensures 1 snapshot per company per day.
        """
        stmt = insert(Upside12MSnapshot).values(**snapshot_data)
        
        # Explicit update fields for ON CONFLICT
        update_dict = {
            "upside_ext_raw": stmt.excluded.upside_ext_raw,
            "rerating_raw": stmt.excluded.rerating_raw,
            "recup_operacional_raw": stmt.excluded.recup_operacional_raw,
            "assimetria_raw": stmt.excluded.assimetria_raw,
            "gov_liq_raw": stmt.excluded.gov_liq_raw,
            "penalties_raw": stmt.excluded.penalties_raw,
            "final_score": stmt.excluded.final_score,
            "bucket": stmt.excluded.bucket,
            "rating_class": stmt.excluded.rating_class,
            "summary": stmt.excluded.summary,
            "model_version": stmt.excluded.model_version
        }
        
        stmt = stmt.on_conflict_do_update(
            index_elements=["company_id", "as_of_date"],
            set_=update_dict
        ).returning(Upside12MSnapshot)
        
        result = self.db.execute(stmt).scalar_one()
        return result

    def save_ranking_batch(self, rankings_data: list[dict]):
        """
        Saves the ranking snapshot for a day.
        Deletes existing rankings for the same date first, then inserts fresh.
        This avoids UniqueConstraint conflicts when re-running on the same day
        (e.g. recalibrating after scoring engine updates).
        """
        if not rankings_data:
            return

        as_of_date = rankings_data[0]["as_of_date"]

        # Clean slate for this date before inserting
        self.db.query(Upside12MRanking).filter(
            Upside12MRanking.as_of_date == as_of_date
        ).delete(synchronize_session=False)

        # Insert fresh rows
        for row in rankings_data:
            self.db.add(Upside12MRanking(**row))

    def get_latest_ranking(self) -> list[Upside12MRanking]:
        latest_date = self.db.execute(select(func.max(Upside12MRanking.as_of_date))).scalar()
        
        if not latest_date:
            return []
            
        stmt = select(Upside12MRanking).where(
            Upside12MRanking.as_of_date == latest_date
        ).order_by(Upside12MRanking.position)
        
        return list(self.db.execute(stmt).scalars().all())

    def upsert_research_target(self, target_data: dict) -> ResearchTarget:
        """
        Adds or updates a research target. 
        Logic: if company has a target today, update it; otherwise add new.
        """
        company_id = target_data["company_id"]
        as_of_date = target_data["as_of_date"]
        
        existing = self.db.query(ResearchTarget).filter(
            ResearchTarget.company_id == company_id,
            ResearchTarget.as_of_date == as_of_date
        ).first()
        
        if existing:
            for k, v in target_data.items():
                if hasattr(existing, k) and k != "id":
                    setattr(existing, k, v)
            return existing
        else:
            target = ResearchTarget(**target_data)
            self.db.add(target)
            return target

    def get_latest_ticker_ranking(self, ticker: str) -> Optional[Upside12MRanking]:
        from app.models.company import Company
        latest_date = self.db.execute(select(func.max(Upside12MRanking.as_of_date))).scalar()
        if not latest_date:
            return None
            
        stmt = select(Upside12MRanking).join(Company).where(
            Company.ticker == ticker,
            Upside12MRanking.as_of_date == latest_date
        )
        return self.db.execute(stmt).scalars().first()

    def get_latest_snapshot(self, company_id: str) -> Optional[Upside12MSnapshot]:
        return self.db.query(Upside12MSnapshot).filter(
            Upside12MSnapshot.company_id == company_id
        ).order_by(Upside12MSnapshot.as_of_date.desc()).first()

    def get_research_target(self, company_id: str) -> Optional[ResearchTarget]:
        return self.db.query(ResearchTarget).filter(
            ResearchTarget.company_id == company_id
        ).order_by(ResearchTarget.as_of_date.desc()).first()
