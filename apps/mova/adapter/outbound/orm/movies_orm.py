"""@see docs/DevOps/suvisdev/ENTITY_RULE.md — 영화 정보 (HOT 랭킹·상세용)."""

import re

from sqlalchemy import Float, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from mova.adapter.outbound.orm.base_orm import MovaModel


def slugify_movie(title: str) -> str:
    s = re.sub(r"[^\w\s-]", "", title.strip().lower())
    s = re.sub(r"[\s_]+", "-", s).strip("-")
    return s[:64] or "movie"


class MovaMovie(MovaModel):
    """영화 정보. PK `id` — 상세·랭킹은 `movie_id` FK로 참조."""

    __tablename__ = "movies"

    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    release_year: Mapped[str] = mapped_column(String(8), nullable=False, default="")
    rating: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    poster_url: Mapped[str] = mapped_column(Text, nullable=False, default="")
    platform: Mapped[str | None] = mapped_column(String(16), nullable=True)
    genres: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
