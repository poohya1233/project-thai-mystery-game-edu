from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.connection import get_db
from models.player_profile import PlayerProfile
from models.player_progress import PlayerProgress
from schemas.player import (
    EnergyState,
    PlayerProfileOut,
    StageProgressOut,
    StreakState,
)
from services.energy_service import get_bangkok_today, sync_daily_energy
from services.streak_service import update_daily_streak

router = APIRouter(prefix="/players", tags=["Player"])


def _get_profile_or_404(db: Session, user_id: int) -> PlayerProfile:
    profile = db.scalar(select(PlayerProfile).where(PlayerProfile.user_id == user_id))
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player profile not found")
    return profile


@router.get("/{user_id}/profile", response_model=PlayerProfileOut)
def get_player_profile(user_id: int, db: Session = Depends(get_db)):
    profile = _get_profile_or_404(db, user_id)
    today = get_bangkok_today()
    sync_daily_energy(profile, today=today)
    update_daily_streak(profile, today=today)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{user_id}/energy", response_model=EnergyState)
def get_player_energy(user_id: int, db: Session = Depends(get_db)):
    profile = _get_profile_or_404(db, user_id)
    sync_daily_energy(profile, today=get_bangkok_today())
    db.commit()
    db.refresh(profile)
    return EnergyState(
        energy=profile.energy,
        max_energy=profile.max_energy,
        energy_cost_per_answer=profile.energy_cost_per_answer,
        daily_questions_answered=profile.daily_questions_answered,
        daily_question_limit=profile.daily_question_limit,
        energy_reset_date=profile.energy_reset_date,
    )


@router.get("/{user_id}/streak", response_model=StreakState)
def get_player_streak(user_id: int, db: Session = Depends(get_db)):
    profile = _get_profile_or_404(db, user_id)
    update_daily_streak(profile, today=get_bangkok_today())
    db.commit()
    db.refresh(profile)
    return StreakState(
        streak_count=profile.streak_count,
        best_streak=profile.best_streak,
        last_streak_date=profile.last_streak_date,
    )


@router.get("/{user_id}/progress", response_model=list[StageProgressOut])
def get_player_progress(user_id: int, db: Session = Depends(get_db)):
    profile = _get_profile_or_404(db, user_id)
    records = db.scalars(
        select(PlayerProgress)
        .where(PlayerProgress.profile_id == profile.id)
        .order_by(PlayerProgress.stage_id)
    ).all()
    return list(records)