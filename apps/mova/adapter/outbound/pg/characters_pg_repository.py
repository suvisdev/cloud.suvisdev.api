from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from mova.adapter.outbound.orm.actors_orm import MovaActor
from mova.adapter.outbound.orm.characters_orm import MovaCharacter
from mova.adapter.outbound.orm.movies_orm import MovaMovie
from mova.adapter.outbound.pg.pg_session import run_pg
from mova.app.ports.output.characters_repository import CharactersRepository

logger = logging.getLogger(__name__)


class CharactersRepositoryError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class CharactersPgRepository(CharactersRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def _get_movie(self, session, movie_id: int) -> MovaMovie | None:
        result = await session.execute(select(MovaMovie).where(MovaMovie.id == movie_id))
        return result.scalar_one_or_none()

    async def _get_actor(self, session, actor_id: int) -> MovaActor | None:
        result = await session.execute(select(MovaActor).where(MovaActor.id == actor_id))
        return result.scalar_one_or_none()

    async def link(self, movie_id: int, actor_id: int) -> MovaCharacter:
        logger.info(
            "[CharactersPgRepository] link — movie_id=%s actor_id=%s",
            movie_id,
            actor_id,
        )

        async def work(session: AsyncSession) -> MovaCharacter:
            if await self._get_movie(session, movie_id) is None:
                raise CharactersRepositoryError(
                    f"영화 ID {movie_id}를 찾을 수 없습니다.",
                    status_code=404,
                )
            if await self._get_actor(session, actor_id) is None:
                raise CharactersRepositoryError(
                    f"인물 ID {actor_id}를 찾을 수 없습니다.",
                    status_code=404,
                )

            result = await session.execute(
                select(MovaCharacter).where(
                    MovaCharacter.movie_id == movie_id,
                    MovaCharacter.actor_id == actor_id,
                ),
            )
            row = result.scalar_one_or_none()
            if row is not None:
                return row

            row = MovaCharacter(movie_id=movie_id, actor_id=actor_id)
            session.add(row)
            try:
                await session.flush()
                await session.refresh(row)
            except IntegrityError as e:
                await session.rollback()
                raise CharactersRepositoryError(
                    "영화–인물 연결 저장에 실패했습니다.",
                    status_code=409,
                ) from e
            return row

        return await run_pg(self._session, work)

    async def unlink(self, link_id: int) -> bool:
        async def work(session: AsyncSession) -> bool:
            result = await session.execute(
                select(MovaCharacter).where(MovaCharacter.id == link_id),
            )
            row = result.scalar_one_or_none()
            if row is None:
                raise CharactersRepositoryError(
                    f"연결 ID {link_id}를 찾을 수 없습니다.",
                    status_code=404,
                )
            await session.delete(row)
            return True

        return await run_pg(self._session, work)

    async def list_links(
        self,
        *,
        movie_id: int | None = None,
        actor_id: int | None = None,
        limit: int = 100,
    ) -> list[MovaCharacter]:
        async def work(session: AsyncSession) -> list[MovaCharacter]:
            stmt = select(MovaCharacter).order_by(MovaCharacter.id.desc())
            if movie_id is not None:
                stmt = stmt.where(MovaCharacter.movie_id == movie_id)
            if actor_id is not None:
                stmt = stmt.where(MovaCharacter.actor_id == actor_id)
            result = await session.execute(stmt.limit(limit))
            return list(result.scalars().all())

        return await run_pg(self._session, work)

    async def list_actors_by_movie(
        self,
        movie_id: int,
        limit: int = 100,
    ) -> list[tuple[MovaCharacter, MovaActor]]:
        async def work(session: AsyncSession) -> list[tuple[MovaCharacter, MovaActor]]:
            if await self._get_movie(session, movie_id) is None:
                raise CharactersRepositoryError(
                    f"영화 ID {movie_id}를 찾을 수 없습니다.",
                    status_code=404,
                )
            result = await session.execute(
                select(MovaCharacter, MovaActor)
                .join(MovaActor, MovaCharacter.actor_id == MovaActor.id)
                .where(MovaCharacter.movie_id == movie_id)
                .order_by(MovaActor.name.asc())
                .limit(limit),
            )
            return [(row[0], row[1]) for row in result.all()]

        return await run_pg(self._session, work)

    async def list_movies_by_actor(
        self,
        actor_id: int,
        limit: int = 100,
    ) -> list[tuple[MovaCharacter, MovaMovie]]:
        async def work(session: AsyncSession) -> list[tuple[MovaCharacter, MovaMovie]]:
            if await self._get_actor(session, actor_id) is None:
                raise CharactersRepositoryError(
                    f"인물 ID {actor_id}를 찾을 수 없습니다.",
                    status_code=404,
                )
            result = await session.execute(
                select(MovaCharacter, MovaMovie)
                .join(MovaMovie, MovaCharacter.movie_id == MovaMovie.id)
                .where(MovaCharacter.actor_id == actor_id)
                .order_by(MovaMovie.title.asc())
                .limit(limit),
            )
            return [(row[0], row[1]) for row in result.all()]

        return await run_pg(self._session, work)
