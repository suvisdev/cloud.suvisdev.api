"""@see docs/DevOps/Backend/ENTITY_RULE.md — 사용자↔영화 상호작용(취향 분석용)."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from mova.app.models.base import MovaModel

# 찜하기 / 시청완료 / 클릭 / 관심 없음
ACTION_FAVORITE = "favorite"
ACTION_WATCHED = "watched"
ACTION_CLICK = "click"
ACTION_NOT_INTERESTED = "not_interested"

VALID_ACTION_TYPES = frozenset(
    {ACTION_FAVORITE, ACTION_WATCHED, ACTION_CLICK, ACTION_NOT_INTERESTED},
)


class MovaInteraction(MovaModel):
    """사용자의 영화 반응 기록. PK `id` — AI 취향 분석 입력."""

    __tablename__ = "interactions"

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    movie_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    action_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
