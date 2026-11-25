from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class EnergyState(BaseModel):
    energy: int
    max_energy: int
    energy_cost_per_answer: int
    daily_questions_answered: int
    daily_question_limit: int | None = None
    energy_reset_date: date | None = None


class StreakState(BaseModel):
    streak_count: int
    best_streak: int
    last_streak_date: date | None = None


class PlayerProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    energy: int
    max_energy: int
    energy_cost_per_answer: int
    daily_questions_answered: int
    daily_question_limit: int | None = None
    energy_reset_date: date | None = None
    streak_count: int
    best_streak: int
    last_streak_date: date | None = None
    total_score: int
    current_chapter_id: int | None = None
    updated_at: datetime


class StageProgressOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    stage_id: int
    is_unlocked: bool
    is_completed: bool
    watched_3d_intro: bool
    best_score: int
    attempts_count: int
    last_played_at: datetime | None = None
    completed_at: datetime | None = None
