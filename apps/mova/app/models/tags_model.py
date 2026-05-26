"""@see docs/DevOps/Backend/ENTITY_RULE.md — 영화별 키워드 태그 (감성·장르·등장인물)."""

import re

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from mova.app.models.base import MovaModel

TAG_KIND_MOOD = "mood"
TAG_KIND_GENRE = "genre"
TAG_KIND_CAST = "cast"
TAG_KINDS = frozenset({TAG_KIND_MOOD, TAG_KIND_GENRE, TAG_KIND_CAST})


def slugify_tag(label: str) -> str:
    s = re.sub(r"[^\w\s-]", "", label.strip().lower())
    s = re.sub(r"[\s_]+", "-", s).strip("-")
    return s[:64] or "tag"


class MovaTag(MovaModel):
    """영화 키워드: 감성(mood), 장르(genre), 등장인물(cast)."""

    __tablename__ = "tags"
    __table_args__ = (
        UniqueConstraint("movie_id", "slug", name="uq_tags_movie_slug"),
        UniqueConstraint("character_id", name="uq_tags_character_id"),
    )

    movie_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    character_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="cast 태그일 때 characters.id (영화–인물 연결)",
    )
    tag_kind: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=TAG_KIND_MOOD,
        index=True,
        comment="mood | genre | cast",
    )
    slug: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
