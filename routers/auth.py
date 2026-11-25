import hashlib
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.connection import get_db
from models.game.chapter import Chapter
from models.game.stage import Stage
from models.player_profile import PlayerProfile
from models.user import User
from schemas.auth import UserLogin, UserOut, UserRegister
from schemas.player import PlayerProfileOut
from services.energy_service import get_bangkok_today, sync_daily_energy
from services.game_service import get_or_create_stage_progress
from services.streak_service import update_daily_streak

router = APIRouter(prefix="/auth", tags=["Auth"])


def _hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return f"{salt}${digest.hex()}"


def _verify_password(plain_password: str, stored_hash: str) -> bool:
    try:
        salt, hex_digest = stored_hash.split("$", 1)
    except ValueError:
        return False
    candidate = _hash_password(plain_password, salt=salt).split("$", 1)[1]
    return secrets.compare_digest(candidate, hex_digest)


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.scalar(select(User).where(User.username == payload.username))
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    if payload.email is not None:
        existing_email = db.scalar(select(User).where(User.email == payload.email))
        if existing_email is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    first_chapter = db.scalar(
        select(Chapter).where(Chapter.is_active.is_(True)).order_by(Chapter.chapter_number)
    )
    today = get_bangkok_today()

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=_hash_password(payload.password),
        is_active=True,
    )
    db.add(user)
    db.flush()

    profile = PlayerProfile(
        user_id=user.id,
        energy_reset_date=today,
        last_streak_date=today,
        streak_count=1,
        best_streak=1,
        current_chapter_id=first_chapter.id if first_chapter else None,
    )
    db.add(profile)
    db.flush()

    if first_chapter is not None:
        first_stage = db.scalar(
            select(Stage)
            .where(Stage.chapter_id == first_chapter.id, Stage.is_active.is_(True))
            .order_by(Stage.stage_number)
        )
        if first_stage is not None:
            get_or_create_stage_progress(db, profile, first_stage, is_unlocked=True)

    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=PlayerProfileOut)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == payload.username))
    if user is None or not _verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")

    profile = db.scalar(select(PlayerProfile).where(PlayerProfile.user_id == user.id))
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player profile not found")

    today = get_bangkok_today()
    sync_daily_energy(profile, today=today)
    update_daily_streak(profile, today=today)
    db.commit()
    db.refresh(profile)
    return profile