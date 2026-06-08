"""@see docs/DevOps/suvisdev/ENTITY_RULE.md — AI 채팅 추천 작품 기록 (`picks`)."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from mova.adapter.outbound.orm.base_orm import MovaModel
from viewer.app.dtos.user_model import User


class MovaPick(MovaModel):
    """한 번의 AI 채팅 응답에서 추천된 작품 1편 (보통 3행/응답)."""

    __tablename__ = "picks"

    chat_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("chat.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(User.__table__.c.id, ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Secom users.id (동일 DB FK, 비로그인 NULL)",
    )
    movie_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    pick_rank: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="해당 응답 내 순위 1~3",
    )
    hook: Mapped[str | None] = mapped_column(String(120), nullable=True)
    title_snapshot: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="추천 시점 제목 (DB slug 보강 전후 스냅샷)",
    )
    batch_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="동일 채팅 응답 3편 묶음 시각",
    )
