from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.connection import get_db
from schemas.leaderboard import LeaderboardListOut
from services.leaderboard_service import get_full_leaderboard

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get("", response_model=LeaderboardListOut)
def read_leaderboard(db: Session = Depends(get_db)):
    return get_full_leaderboard(db)