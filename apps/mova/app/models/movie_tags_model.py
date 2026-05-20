"""@see docs/DevOps/Backend/ENTITY_RULE.md — 감성 태그·영화 연결."""

import re

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from mova.app.models.base import MovaModel


def slugify_tag(label: str) -> str:
    s = re.sub(r"[^\w\s-]", "", label.strip().lower())
    s = re.sub(r"[\s_]+", "-", s).strip("-")
    return s[:64] or "tag"


class MovaTag(MovaModel):
    """감성·분위기 태그. 예: '우울할 때 위로되는 영화'. PK `id`."""

    __tablename__ = "tags"

    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")


class MovaMovieTag(MovaModel):
    """영화–감성 태그 다대다 중간 테이블."""

    __tablename__ = "movie_tags"
    __table_args__ = (
        UniqueConstraint("movie_id", "tag_id", name="uq_movie_tags_movie_tag"),
    )

    movie_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tag_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tags.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
