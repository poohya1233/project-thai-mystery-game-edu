from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from models.player_progress import PlayerProgress
    from models.user import User


class PlayerProfile(Base):
    __tablename__ = "player_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    # ระบบพลังงานชีวิต (ลดทุกครั้งที่ตอบคำถาม ไม่ว่าถูกหรือผิด)
    energy: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    max_energy: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    energy_cost_per_answer: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    daily_questions_answered: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    daily_question_limit: Mapped[int | None] = mapped_column(Integer, default=None, nullable=True)
    energy_reset_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # ระบบเติมไฟรายวัน (Daily Streak)
    streak_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    best_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_streak_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # ความคืบหน้าและคะแนนรวม
    total_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_chapter_id: Mapped[int | None] = mapped_column(
        ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="profile")
    progress_records: Mapped[list["PlayerProgress"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )