from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from mova.domain.value_objects.movie_catalog import resolve_canonical_slug
from mova.adapter.outbound.orm.movies_orm import MovaMovie, slugify_movie
from mova.adapter.outbound.pg.pg_session import run_pg
from mova.app.dtos.movies_dto import MovieTitleCommand, MovieUpsertCommand
from mova.app.ports.output.movies_repository import MoviesRepository

logger = logging.getLogger(__name__)


class MoviesRepositoryError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class MoviesPgRepository(MoviesRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def get_by_id(self, movie_id: int) -> MovaMovie | None:
        async def work(session: AsyncSession) -> MovaMovie | None:
            result = await session.execute(select(MovaMovie).where(MovaMovie.id == movie_id))
            return result.scalar_one_or_none()

        return await run_pg(self._session, work)

    async def get_by_slug(self, slug: str) -> MovaMovie | None:
        key = slug.strip()
        if not key:
            return None

        async def work(session: AsyncSession) -> MovaMovie | None:
            result = await session.execute(select(MovaMovie).where(MovaMovie.slug == key))
            return result.scalar_one_or_none()

        return await run_pg(self._session, work)

    async def find_by_title(self, title: str) -> MovaMovie | None:
        key = title.strip()
        if not key:
            return None

        async def work(session: AsyncSession) -> MovaMovie | None:
            exact = await session.execute(
                select(MovaMovie).where(MovaMovie.title == key[:255]).limit(1),
            )
            row = exact.scalar_one_or_none()
            if row is not None:
                return row
            fuzzy = await session.execute(
                select(MovaMovie).where(MovaMovie.title.ilike(f"%{key}%")).limit(1),
            )
            return fuzzy.scalar_one_or_none()

        return await run_pg(self._session, work)

    async def upsert(self, command: MovieUpsertCommand) -> MovaMovie:
        title = command.title.strip()
        if not title:
            raise MoviesRepositoryError("영화 제목이 비어 있습니다.", status_code=400)

        slug = (
            str(command.slug or "").strip()
            or resolve_canonical_slug(title)
            or slugify_movie(title)
        )
        slug = slug[:64]

        logger.info("[MoviesPgRepository] upsert — slug=%r title=%r", slug, title)

        async def work(session: AsyncSession) -> MovaMovie:
            result = await session.execute(select(MovaMovie).where(MovaMovie.slug == slug))
            row = result.scalar_one_or_none()
            if row is None:
                row = MovaMovie(
                    slug=slug,
                    title=title[:255],
                    release_year=command.release_year.strip()[:8],
                    rating=float(command.rating),
                    poster_url=command.poster.strip(),
                    platform=command.platform,
                    genres=list(command.genres or []),
                )
                session.add(row)
            else:
                row.title = title[:255]
                row.release_year = command.release_year.strip()[:8] or row.release_year
                row.rating = float(command.rating)
                new_poster = command.poster.strip()
                if new_poster:
                    row.poster_url = new_poster
                if command.platform is not None:
                    row.platform = command.platform
                if command.genres is not None:
                    row.genres = list(command.genres or [])

            try:
                await session.flush()
                await session.refresh(row)
            except IntegrityError as e:
                await session.rollback()
                raise MoviesRepositoryError(
                    "영화 저장에 실패했습니다. slug가 중복일 수 있습니다.",
                    status_code=409,
                ) from e
            return row

        return await run_pg(self._session, work)

    async def upsert_title(self, command: MovieTitleCommand) -> int:
        row = await self.upsert(MovieUpsertCommand(title=command.title))
        return row.id

    async def upsert_titles(self, commands: list[MovieTitleCommand]) -> list[int]:
        ids: list[int] = []
        seen: set[str] = set()
        for command in commands:
            key = command.title.strip()
            if not key or key in seen:
                continue
            seen.add(key)
            ids.append(await self.upsert_title(MovieTitleCommand(title=key)))
        return ids

    async def list_movies(self, limit: int = 100) -> list[MovaMovie]:
        async def work(session: AsyncSession) -> list[MovaMovie]:
            result = await session.execute(
                select(MovaMovie).order_by(MovaMovie.id.desc()).limit(limit),
            )
            return list(result.scalars().all())

        return await run_pg(self._session, work)

    async def list_titles(self, limit: int = 100) -> list[MovaMovie]:
        return await self.list_movies(limit=limit)
