from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from models.game.chapter import Chapter
    from models.game.question import Question
    from models.player_progress import PlayerProgress


class Stage(Base):
    __tablename__ = "stages"
    __table_args__ = (
        UniqueConstraint("chapter_id", "stage_number", name="uq_chapter_stage_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    chapter_id: Mapped[int] = mapped_column(
        ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    stage_number: Mapped[int] = mapped_column(Integer, nullable=False)  # 5-10 ด่านต่อบท
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    instruction: Mapped[str | None] = mapped_column(Text, nullable=True)
    reward_score: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    chapter: Mapped["Chapter"] = relationship(back_populates="stages")
    questions: Mapped[list["Question"]] = relationship(
        back_populates="stage",
        order_by="Question.order_index",
        cascade="all, delete-orphan",
    )
    player_progress: Mapped[list["PlayerProgress"]] = relationship(
        back_populates="stage", cascade="all, delete-orphan"
    )