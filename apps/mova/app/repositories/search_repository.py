import logging
from dataclasses import dataclass
from typing import Literal

from sqlalchemy import String, cast, or_, select

from database import get_session_factory
from mova.app.models.actors_model import MovaActor
from mova.app.models.movie_characters_model import MovaMovieCharacter
from mova.app.models.movie_tags_model import MovaMovieTag, MovaTag
from mova.app.models.movies_model import MovaMovie

logger = logging.getLogger(__name__)

MatchType = Literal["title", "person", "keyword", "synopsis"]
_MATCH_PRIORITY: dict[MatchType, int] = {
    "title": 0,
    "person": 1,
    "keyword": 2,
    "synopsis": 3,
}


@dataclass(frozen=True)
class SearchHit:
    movie: MovaMovie
    match_type: MatchType


class SearchRepository:
    async def search(self, query: str, *, limit: int = 12) -> list[SearchHit]:
        q = query.strip()
        if not q:
            return []

        pattern = f"%{q}%"
        cap = max(limit * 3, 24)
        merged: dict[int, SearchHit] = {}

        def _merge(movie: MovaMovie, match_type: MatchType) -> None:
            existing = merged.get(movie.id)
            if existing is None or _MATCH_PRIORITY[match_type] < _MATCH_PRIORITY[existing.match_type]:
                merged[movie.id] = SearchHit(movie=movie, match_type=match_type)

        factory = get_session_factory()
        async with factory() as session:
            title_rows = await session.execute(
                select(MovaMovie)
                .where(
                    or_(
                        MovaMovie.title.ilike(pattern),
                        MovaMovie.slug.ilike(pattern),
                    ),
                )
                .order_by(MovaMovie.rating.desc(), MovaMovie.id.desc())
                .limit(cap),
            )
            for movie in title_rows.scalars():
                _merge(movie, "title")

            person_rows = await session.execute(
                select(MovaMovie)
                .join(MovaMovieCharacter, MovaMovieCharacter.movie_id == MovaMovie.id)
                .join(MovaActor, MovaActor.id == MovaMovieCharacter.actor_id)
                .where(MovaActor.name.ilike(pattern))
                .order_by(MovaMovie.rating.desc(), MovaMovie.id.desc())
                .limit(cap),
            )
            for movie in person_rows.scalars().unique():
                _merge(movie, "person")

            tag_rows = await session.execute(
                select(MovaMovie)
                .join(MovaMovieTag, MovaMovieTag.movie_id == MovaMovie.id)
                .join(MovaTag, MovaTag.id == MovaMovieTag.tag_id)
                .where(
                    or_(
                        MovaTag.label.ilike(pattern),
                        MovaTag.description.ilike(pattern),
                    ),
                )
                .order_by(MovaMovie.rating.desc(), MovaMovie.id.desc())
                .limit(cap),
            )
            for movie in tag_rows.scalars().unique():
                _merge(movie, "keyword")

            genre_rows = await session.execute(
                select(MovaMovie)
                .where(cast(MovaMovie.genres, String).ilike(pattern))
                .order_by(MovaMovie.rating.desc(), MovaMovie.id.desc())
                .limit(cap),
            )
            for movie in genre_rows.scalars():
                _merge(movie, "keyword")

        ordered = sorted(
            merged.values(),
            key=lambda h: (_MATCH_PRIORITY[h.match_type], -h.movie.rating, -h.movie.id),
        )
        logger.info("[SearchRepository] search — q=%r hits=%s", q, len(ordered[:limit]))
        return ordered[:limit]
