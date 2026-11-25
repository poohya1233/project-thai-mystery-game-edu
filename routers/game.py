from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from database.connection import get_db
from models.game.chapter import Chapter
from models.game.question import Question
from models.game.stage import Stage
from models.player_profile import PlayerProfile
from schemas.game import (
    AnswerSubmitIn,
    AnswerSubmitOut,
    ChapterOut,
    QuestionOut,
    StageOut,
)
from schemas.player import StageProgressOut
from services.energy_service import DailyQuestionLimitError, InsufficientEnergyError
from services.game_service import get_or_create_stage_progress, submit_question_answer

router = APIRouter(prefix="/game", tags=["Game"])


@router.get("/chapters", response_model=list[ChapterOut])
def list_chapters(db: Session = Depends(get_db)):
    chapters = db.scalars(
        select(Chapter)
        .where(Chapter.is_active.is_(True))
        .options(selectinload(Chapter.stages))
        .order_by(Chapter.chapter_number)
    ).all()

    result: list[ChapterOut] = []
    for ch in chapters:
        active_stages = sorted(
            [s for s in ch.stages if s.is_active],
            key=lambda s: s.stage_number,
        )
        result.append(
            ChapterOut(
                id=ch.id,
                chapter_number=ch.chapter_number,
                title=ch.title,
                description=ch.description,
                intro_3d_scene_key=ch.intro_3d_scene_key,
                intro_3d_duration_sec=ch.intro_3d_duration_sec,
                stages=[StageOut.model_validate(s) for s in active_stages],
            )
        )
    return result


@router.get("/chapters/{chapter_id}/stages", response_model=list[StageOut])
def list_chapter_stages(chapter_id: int, db: Session = Depends(get_db)):
    chapter = db.get(Chapter, chapter_id)
    if chapter is None or not chapter.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    stages = db.scalars(
        select(Stage)
        .where(Stage.chapter_id == chapter_id, Stage.is_active.is_(True))
        .order_by(Stage.stage_number)
    ).all()
    return [StageOut.model_validate(s) for s in stages]


@router.get("/stages/{stage_id}/questions", response_model=list[QuestionOut])
def list_stage_questions(stage_id: int, db: Session = Depends(get_db)):
    stage = db.get(Stage, stage_id)
    if stage is None or not stage.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stage not found")

    questions = db.scalars(
        select(Question)
        .where(Question.stage_id == stage_id)
        .order_by(Question.order_index, Question.id)
    ).all()
    return [QuestionOut.model_validate(q) for q in questions]


@router.post("/stages/{stage_id}/intro-watched", response_model=StageProgressOut)
def mark_3d_intro_watched(stage_id: int, user_id: int, db: Session = Depends(get_db)):
    stage = db.get(Stage, stage_id)
    if stage is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stage not found")

    profile = db.scalar(select(PlayerProfile).where(PlayerProfile.user_id == user_id))
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player profile not found")

    progress = get_or_create_stage_progress(db, profile, stage, is_unlocked=True)
    progress.watched_3d_intro = True
    db.commit()
    db.refresh(progress)
    return StageProgressOut.model_validate(progress)


@router.post("/answer", response_model=AnswerSubmitOut)
def submit_answer(
    user_id: int,
    payload: AnswerSubmitIn,
    db: Session = Depends(get_db),
):
    profile = db.scalar(select(PlayerProfile).where(PlayerProfile.user_id == user_id))
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player profile not found")

    question = db.get(Question, payload.question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    try:
        result = submit_question_answer(
            db=db,
            profile=profile,
            question=question,
            selected_answer=payload.selected_answer,
        )
    except InsufficientEnergyError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except DailyQuestionLimitError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc)) from exc

    return AnswerSubmitOut(**result)