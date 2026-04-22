from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.score_repo import ScoreRepository
from app.schemas.score import ScoreOut

router = APIRouter(prefix="/scores", tags=["scores"])


@router.get("/{ticker}", response_model=ScoreOut)
def get_score_detail(ticker: str, db: Session = Depends(get_db)):
    repo = ScoreRepository(db)
    score = repo.get_latest_by_ticker(ticker)
    if not score:
        raise HTTPException(status_code=404, detail="Score não encontrado")
    return score
