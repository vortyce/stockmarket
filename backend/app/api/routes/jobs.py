from fastapi import APIRouter

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/recalculate")
def trigger_recalculate():
    return {"status": "queued", "job": "recalculate_scores"}
