from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.game.question import Question
from models.game.stage import Stage
from models.player_profile import PlayerProfile
from models.player_progress import PlayerProgress
from services.energy_service import consume_energy_for_answer
from services.streak_service import update_daily_streak


def get_or_create_stage_progress(
    db: Session,
    profile: PlayerProfile,
    stage: Stage,
    is_unlocked: bool = False,
) -> PlayerProgress:
    progress = db.scalar(
        select(PlayerProgress).where(
            PlayerProgress.profile_id == profile.id,
            PlayerProgress.stage_id == stage.id,
        )
    )
    if progress is None:
        progress = PlayerProgress(
            profile_id=profile.id,
            stage_id=stage.id,
            is_unlocked=is_unlocked,
            is_completed=False,
            watched_3d_intro=False,
            best_score=0,
            attempts_count=0,
        )
        db.add(progress)
        db.flush()
    elif is_unlocked and not progress.is_unlocked:
        progress.is_unlocked = True
    return progress


def unlock_next_stage_in_chapter(
    db: Session, profile: PlayerProfile, current_stage: Stage
) -> None:
    next_stage = db.scalar(
        select(Stage).where(
            Stage.chapter_id == current_stage.chapter_id,
            Stage.stage_number == current_stage.stage_number + 1,
            Stage.is_active.is_(True),
        )
    )
    if next_stage is not None:
        get_or_create_stage_progress(db, profile, next_stage, is_unlocked=True)


def submit_question_answer(
    db: Session,
    profile: PlayerProfile,
    question: Question,
    selected_answer: str,
) -> dict:
    """ตรวจคำตอบ หักพลังงานทุกครั้งที่ตอบ และอัปเดตความคืบหน้าด่าน"""
    now = datetime.now(timezone.utc)

    update_daily_streak(profile, today=now.astimezone().date())
    consume_energy_for_answer(profile, today=now.astimezone().date())

    is_correct = selected_answer.strip() == question.correct_answer.strip()
    earned_score = question.points if is_correct else 0

    stage = db.get(Stage, question.stage_id)
    if stage is not None:
        progress = get_or_create_stage_progress(db, profile, stage, is_unlocked=True)
        progress.attempts_count += 1
        progress.last_played_at = now
        if is_correct:
            progress.is_completed = True
            progress.completed_at = progress.completed_at or now
            if earned_score > progress.best_score:
                progress.best_score = earned_score
            profile.total_score += earned_score
            unlock_next_stage_in_chapter(db, profile, stage)

    recalculate_leaderboard(db)
    db.commit()
    db.refresh(profile)

    return {
        "is_correct": is_correct,
        "earned_score": earned_score,
        "correct_answer": question.correct_answer,
        "explanation": question.explanation,
        "remaining_energy": profile.energy,
        "daily_questions_answered": profile.daily_questions_answered,
        "can_retry_stage": True,
    }