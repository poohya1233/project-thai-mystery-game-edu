from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from models.game.stage import Stage


class Chapter(Base):
    __tablename__ = "chapters"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    chapter_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)  # 1..5
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ข้อมูลแอนิเมชัน 3 มิติก่อนเริ่มต้นบท (ให้ Godot 4 นำไปเรียก scene/animation)
    intro_3d_scene_key: Mapped[str | None] = mapped_column(String(120), nullable=True)
    intro_3d_duration_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    stages: Mapped[list["Stage"]] = relationship(
        back_populates="chapter",
        order_by="Stage.stage_number",
        cascade="all, delete-orphan",
    )