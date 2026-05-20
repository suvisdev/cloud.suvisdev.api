"""@see docs/DevOps/Backend/ENTITY_RULE.md — Mova 취향 분석용 사용자 프로필."""

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from mova.app.models.base import MovaModel


class MovaUser(MovaModel):
    """Mova AI 취향 분석 대상 사용자. PK `id`."""

    __tablename__ = "users"

    nickname: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    preferred_genres: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
