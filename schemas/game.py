from pydantic import BaseModel, ConfigDict, Field


class QuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    stage_id: int
    order_index: int
    prompt: str
    choices: list[str]
    points: int


class StageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chapter_id: int
    stage_number: int
    title: str
    instruction: str | None = None
    reward_score: int


class ChapterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chapter_number: int
    title: str
    description: str | None = None
    intro_3d_scene_key: str | None = None
    intro_3d_duration_sec: int | None = None
    stages: list[StageOut] = []


class AnswerSubmitIn(BaseModel):
    question_id: int
    selected_answer: str = Field(..., min_length=1, max_length=255)


class AnswerSubmitOut(BaseModel):
    is_correct: bool
    earned_score: int
    correct_answer: str
    explanation: str | None = None
    remaining_energy: int
    daily_questions_answered: int
    can_retry_stage: bool
