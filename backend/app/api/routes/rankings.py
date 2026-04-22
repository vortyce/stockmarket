from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.ranking_repo import RankingRepository
from app.schemas.ranking import RankingOut
from datetime import date

router = APIRouter(prefix="/rankings", tags=["rankings"])


@router.get("/top20", response_model=list[RankingOut])
def get_top20(
    scope: str = Query(default="general"),
    as_of_date: date | None = Query(default=None),
    limit: int = Query(default=20),
    db: Session = Depends(get_db),
):
    repo = RankingRepository(db)
    return repo.get_top_rankings(scope=scope, as_of_date=as_of_date, limit=limit)
