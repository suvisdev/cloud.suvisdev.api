"""@see docs/DevOps/Backend/ENTITY_RULE.md — 영화별 감성 태그."""

import re

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from mova.app.models.base import MovaModel


def slugify_tag(label: str) -> str:
    s = re.sub(r"[^\w\s-]", "", label.strip().lower())
    s = re.sub(r"[\s_]+", "-", s).strip("-")
    return s[:64] or "tag"


class MovaTag(MovaModel):
    """영화에 붙인 감성 태그 (`tags` 테이블)."""

    __tablename__ = "tags"
    __table_args__ = (
        UniqueConstraint("movie_id", "slug", name="uq_tags_movie_slug"),
    )

    movie_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    slug: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
