from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.sector import SectorConfig


class SectorConfigRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        stmt = select(SectorConfig).order_by(SectorConfig.sector)
        return self.db.execute(stmt).scalars().all()

    def get_by_sector(self, sector: str):
        stmt = select(SectorConfig).where(SectorConfig.sector == sector.upper())
        return self.db.execute(stmt).scalar_one_or_none()
