from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from models.game.stage import Stage
    from models.player_profile import PlayerProfile


class PlayerProgress(Base):
    __tablename__ = "player_progress"
    __table_args__ = (
        UniqueConstraint("profile_id", "stage_id", name="uq_profile_stage_progress"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("player_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    stage_id: Mapped[int] = mapped_column(
        ForeignKey("stages.id", ondelete="CASCADE"), nullable=False, index=True
    )

    is_unlocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    watched_3d_intro: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    best_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    attempts_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    last_played_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    profile: Mapped["PlayerProfile"] = relationship(back_populates="progress_records")
    stage: Mapped["Stage"] = relationship(back_populates="player_progress")