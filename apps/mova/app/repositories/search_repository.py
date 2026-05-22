import logging
from dataclasses import dataclass
from typing import Any, Literal

from sqlalchemy import String, cast, or_, select

from database import get_session_factory
from mova.app.models.actors_model import MovaActor
from mova.app.models.characters_model import MovaCharacter
from mova.app.models.tags_model import MovaTag
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
                .join(MovaCharacter, MovaCharacter.movie_id == MovaMovie.id)
                .join(MovaActor, MovaActor.id == MovaCharacter.actor_id)
                .where(MovaActor.name.ilike(pattern))
                .order_by(MovaMovie.rating.desc(), MovaMovie.id.desc())
                .limit(cap),
            )
            for movie in person_rows.scalars().unique():
                _merge(movie, "person")

            tag_rows = await session.execute(
                select(MovaMovie)
                .join(MovaTag, MovaTag.movie_id == MovaMovie.id)
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

    async def _movie_ids_by_actor(self, session, name: str) -> set[int]:
        pattern = f"%{name.strip()}%"
        if not pattern.strip("%"):
            return set()
        rows = await session.execute(
            select(MovaMovie.id)
            .join(MovaCharacter, MovaCharacter.movie_id == MovaMovie.id)
            .join(MovaActor, MovaActor.id == MovaCharacter.actor_id)
            .where(MovaActor.name.ilike(pattern))
            .distinct(),
        )
        return set(rows.scalars().all())

    async def _movie_ids_by_genre(self, session, genre: str) -> set[int]:
        pattern = f"%{genre.strip()}%"
        if not pattern.strip("%"):
            return set()
        rows = await session.execute(
            select(MovaMovie.id).where(cast(MovaMovie.genres, String).ilike(pattern)),
        )
        return set(rows.scalars().all())

    async def _movie_ids_by_tag_keyword(self, session, keyword: str) -> set[int]:
        pattern = f"%{keyword.strip()}%"
        if not pattern.strip("%"):
            return set()
        rows = await session.execute(
            select(MovaMovie.id)
            .join(MovaTag, MovaTag.movie_id == MovaMovie.id)
            .where(
                or_(
                    MovaTag.label.ilike(pattern),
                    MovaTag.description.ilike(pattern),
                ),
            )
            .distinct(),
        )
        return set(rows.scalars().all())

    async def _hits_from_movie_ids(
        self,
        session,
        movie_ids: set[int],
        *,
        limit: int,
        match_type: MatchType = "keyword",
    ) -> list[SearchHit]:
        if not movie_ids:
            return []
        rows = await session.execute(
            select(MovaMovie)
            .where(MovaMovie.id.in_(movie_ids))
            .order_by(MovaMovie.rating.desc(), MovaMovie.id.desc())
            .limit(max(limit * 2, 24)),
        )
        return [SearchHit(movie=m, match_type=match_type) for m in rows.scalars()][:limit]

    async def search_by_filters(
        self,
        search_filters: dict[str, Any],
        *,
        intent_type: str,
        limit: int = 12,
    ) -> list[SearchHit]:
        """`chat.search_filters` 기반 — filter_and는 must 조건 AND(교집합)."""
        must = search_filters.get("must") if isinstance(search_filters.get("must"), dict) else {}
        similar = (
            search_filters.get("similar_to")
            if isinstance(search_filters.get("similar_to"), dict)
            else {}
        )
        actors = [a for a in (must.get("actors") or []) if str(a).strip()]
        genres = [g for g in (must.get("genres") or []) if str(g).strip()]
        must_kw = [k for k in (must.get("keywords") or []) if str(k).strip()]
        anchor_actors = [a for a in (similar.get("actors") or []) if str(a).strip()]

        factory = get_session_factory()
        async with factory() as session:
            if intent_type == "filter_and":
                sets: list[set[int]] = []
                for name in actors:
                    ids = await self._movie_ids_by_actor(session, name)
                    if ids:
                        sets.append(ids)
                for genre in genres:
                    ids = await self._movie_ids_by_genre(session, genre)
                    if ids:
                        sets.append(ids)
                for kw in must_kw:
                    ids = await self._movie_ids_by_tag_keyword(session, kw)
                    if ids:
                        sets.append(ids)

                if not sets:
                    return []

                intersection = sets[0]
                for s in sets[1:]:
                    intersection &= s
                hits = await self._hits_from_movie_ids(
                    session,
                    intersection,
                    limit=limit,
                    match_type="person" if actors else "keyword",
                )
                logger.info(
                    "[SearchRepository] filter_and — actors=%s genres=%s kw=%s hits=%s",
                    actors,
                    genres,
                    must_kw,
                    len(hits),
                )
                return hits

            if intent_type == "similar_person" and anchor_actors:
                merged: dict[int, SearchHit] = {}
                for name in anchor_actors:
                    for hit in await self._hits_from_movie_ids(
                        session,
                        await self._movie_ids_by_actor(session, name),
                        limit=limit,
                        match_type="person",
                    ):
                        merged[hit.movie.id] = hit
                ordered = sorted(
                    merged.values(),
                    key=lambda h: (-h.movie.rating, -h.movie.id),
                )
                logger.info(
                    "[SearchRepository] similar_person — anchors=%s hits=%s",
                    anchor_actors,
                    len(ordered[:limit]),
                )
                return ordered[:limit]

        return []
