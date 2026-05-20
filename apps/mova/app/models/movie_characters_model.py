"""@see docs/DevOps/Backend/ENTITY_RULE.md — 영화↔인물(배우) 다대다 연결."""

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from mova.app.models.base import MovaModel


class MovaMovieCharacter(MovaModel):
    """영화–인물(배우) 중간 테이블. PK `id` — `movie_id` + `actor_id` UNIQUE."""

    __tablename__ = "movie_characters"
    __table_args__ = (
        UniqueConstraint("movie_id", "actor_id", name="uq_movie_characters_movie_actor"),
    )

    movie_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    actor_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("actors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
