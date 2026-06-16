"""영화 PgRepository — MoviesRepositoryPort 구현체."""

from __future__ import annotations

import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from mova.adapter.outbound.orm.studio_actors_orm import MovaActor
from mova.adapter.outbound.orm.studio_characters_orm import MovaCharacter
from mova.adapter.outbound.orm.studio_movies_orm import MovaMovie
from mova.adapter.outbound.orm.studio_tags_orm import MovaTag
from mova.app.dtos.studio_movies_dto import (
    MovieDetailDto,
    MovieFilterQuery,
    MovieListDto,
    MovieListItemDto,
)
from mova.app.ports.output.studio_movies_repository import MoviesRepositoryPort

logger = logging.getLogger(__name__)

# ── 레거시 호환 클래스 — chat_reply.py에서 세션 없이 직접 사용 ──────────────────

class StudioMoviesPgRepository:
    """chat_reply.py 전용 레거시 클래스 — 자체 세션 생성."""

    def __init__(self) -> None:
        from core.matrix.grid_oracle_database_manager import get_mova_session_factory
        self._factory = get_mova_session_factory()

    async def get_by_slug(self, slug: str) -> "MovaMovie | None":
        async with self._factory() as session:
            result = await session.execute(select(MovaMovie).where(MovaMovie.slug == slug))
            return result.scalar_one_or_none()

    async def find_by_title(self, title: str) -> "MovaMovie | None":
        async with self._factory() as session:
            result = await session.execute(
                select(MovaMovie).where(MovaMovie.title == title).limit(1)
            )
            return result.scalar_one_or_none()

    async def save_movie(self, schema: object) -> "MovaMovie":
        from mova.adapter.outbound.orm.studio_movies_orm import slugify_movie as _slugify
        async with self._factory() as session:
            slug = getattr(schema, "slug", None) or _slugify(getattr(schema, "title", ""))
            existing = (
                await session.execute(select(MovaMovie).where(MovaMovie.slug == slug))
            ).scalar_one_or_none()
            if existing is None:
                existing = MovaMovie(
                    slug=slug,
                    title=getattr(schema, "title", ""),
                    release_year=getattr(schema, "release_year", "") or "",
                    rating=float(getattr(schema, "rating", 0) or 0),
                    poster_url=getattr(schema, "poster_url", "") or "",
                    platforms=[
                        p.model_dump() if hasattr(p, "model_dump") else p
                        for p in (getattr(schema, "platforms", None) or [])
                    ],
                    genres=list(getattr(schema, "genres", []) or []),
                )
                session.add(existing)
            else:
                poster = getattr(schema, "poster_url", None)
                if poster:
                    existing.poster_url = poster
            await session.commit()
            await session.refresh(existing)
            return existing


# ── 헥사고날 PgRepository ─────────────────────────────────────────────────────

class MoviesPgRepository(MoviesRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_slug(self, slug: str) -> MovieDetailDto | None:
        movie_q = await self._session.execute(
            select(MovaMovie).where(MovaMovie.slug == slug)
        )
        movie = movie_q.scalar_one_or_none()
        if not movie:
            return None

        char_actor_q = await self._session.execute(
            select(MovaCharacter, MovaActor)
            .join(MovaActor, MovaCharacter.actor_id == MovaActor.id)
            .where(MovaCharacter.movie_id == movie.id)
            .order_by(MovaActor.role_type, MovaActor.name)
        )
        char_actors = char_actor_q.all()

        tags_q = await self._session.execute(
            select(MovaTag)
            .where(MovaTag.movie_id == movie.id)
            .order_by(MovaTag.tag_kind, MovaTag.label)
        )
        tags = list(tags_q.scalars().all())

        logger.debug(
            "[MoviesPgRepository] get_by_slug=%s actors=%d tags=%d",
            slug, len(char_actors), len(tags),
        )
        return MovieDetailDto.from_orm(movie, char_actors, tags)

    async def list_movies(self, query: MovieFilterQuery) -> MovieListDto:
        stmt = select(MovaMovie)
        count_stmt = select(func.count(MovaMovie.id))

        if query.genre:
            cond = MovaMovie.genres.contains([query.genre])
            stmt = stmt.where(cond)
            count_stmt = count_stmt.where(cond)

        if query.release_year:
            cond = MovaMovie.release_year == query.release_year
            stmt = stmt.where(cond)
            count_stmt = count_stmt.where(cond)

        if query.min_rating is not None:
            cond = MovaMovie.rating >= query.min_rating
            stmt = stmt.where(cond)
            count_stmt = count_stmt.where(cond)

        if query.age_rating:
            cond = MovaMovie.age_rating == query.age_rating
            stmt = stmt.where(cond)
            count_stmt = count_stmt.where(cond)

        if query.platform:
            cond = MovaMovie.platforms.contains([{"provider": query.platform}])
            stmt = stmt.where(cond)
            count_stmt = count_stmt.where(cond)

        if query.sort == "rating":
            stmt = stmt.order_by(MovaMovie.rating.desc())
        elif query.sort == "popular":
            stmt = stmt.order_by(MovaMovie.rating.desc())
        else:
            stmt = stmt.order_by(MovaMovie.release_year.desc(), MovaMovie.id.desc())

        total_r = await self._session.execute(count_stmt)
        total = total_r.scalar_one()

        stmt = stmt.limit(query.limit).offset(query.offset)
        movies_r = await self._session.execute(stmt)
        movies = list(movies_r.scalars().all())

        logger.debug(
            "[MoviesPgRepository] list_movies total=%d returned=%d", total, len(movies)
        )
        return MovieListDto(
            items=[MovieListItemDto.from_orm(m) for m in movies],
            total=total,
            limit=query.limit,
            offset=query.offset,
        )
