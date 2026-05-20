import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database import get_session_factory
from mova.app.models.actors_model import MovaActor
from mova.app.models.movie_characters_model import MovaMovieCharacter
from mova.app.models.movies_model import MovaMovie

logger = logging.getLogger(__name__)


class MovieCharactersRepositoryError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class MovieCharactersRepository:
    async def _get_movie(self, session, movie_id: int) -> MovaMovie | None:
        result = await session.execute(select(MovaMovie).where(MovaMovie.id == movie_id))
        return result.scalar_one_or_none()

    async def _get_actor(self, session, actor_id: int) -> MovaActor | None:
        result = await session.execute(select(MovaActor).where(MovaActor.id == actor_id))
        return result.scalar_one_or_none()

    async def link(self, movie_id: int, actor_id: int) -> MovaMovieCharacter:
        logger.info(
            "[MovieCharactersRepository] link — movie_id=%s actor_id=%s",
            movie_id,
            actor_id,
        )
        factory = get_session_factory()
        async with factory() as session:
            if await self._get_movie(session, movie_id) is None:
                raise MovieCharactersRepositoryError(
                    f"영화 ID {movie_id}를 찾을 수 없습니다.",
                    status_code=404,
                )
            if await self._get_actor(session, actor_id) is None:
                raise MovieCharactersRepositoryError(
                    f"인물 ID {actor_id}를 찾을 수 없습니다.",
                    status_code=404,
                )

            result = await session.execute(
                select(MovaMovieCharacter).where(
                    MovaMovieCharacter.movie_id == movie_id,
                    MovaMovieCharacter.actor_id == actor_id,
                ),
            )
            row = result.scalar_one_or_none()
            if row is not None:
                return row

            row = MovaMovieCharacter(movie_id=movie_id, actor_id=actor_id)
            session.add(row)
            try:
                await session.commit()
                await session.refresh(row)
            except IntegrityError as e:
                await session.rollback()
                raise MovieCharactersRepositoryError(
                    "영화–인물 연결 저장에 실패했습니다.",
                    status_code=409,
                ) from e
            return row

    async def unlink(self, link_id: int) -> bool:
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(
                select(MovaMovieCharacter).where(MovaMovieCharacter.id == link_id),
            )
            row = result.scalar_one_or_none()
            if row is None:
                raise MovieCharactersRepositoryError(
                    f"연결 ID {link_id}를 찾을 수 없습니다.",
                    status_code=404,
                )
            await session.delete(row)
            await session.commit()
            return True

    async def list_links(
        self,
        *,
        movie_id: int | None = None,
        actor_id: int | None = None,
        limit: int = 100,
    ) -> list[MovaMovieCharacter]:
        factory = get_session_factory()
        async with factory() as session:
            stmt = select(MovaMovieCharacter).order_by(MovaMovieCharacter.id.desc())
            if movie_id is not None:
                stmt = stmt.where(MovaMovieCharacter.movie_id == movie_id)
            if actor_id is not None:
                stmt = stmt.where(MovaMovieCharacter.actor_id == actor_id)
            result = await session.execute(stmt.limit(limit))
            return list(result.scalars().all())

    async def list_actors_by_movie(
        self,
        movie_id: int,
        limit: int = 100,
    ) -> list[tuple[MovaMovieCharacter, MovaActor]]:
        factory = get_session_factory()
        async with factory() as session:
            if await self._get_movie(session, movie_id) is None:
                raise MovieCharactersRepositoryError(
                    f"영화 ID {movie_id}를 찾을 수 없습니다.",
                    status_code=404,
                )
            result = await session.execute(
                select(MovaMovieCharacter, MovaActor)
                .join(MovaActor, MovaMovieCharacter.actor_id == MovaActor.id)
                .where(MovaMovieCharacter.movie_id == movie_id)
                .order_by(MovaActor.name.asc())
                .limit(limit),
            )
            return [(row[0], row[1]) for row in result.all()]

    async def list_movies_by_actor(
        self,
        actor_id: int,
        limit: int = 100,
    ) -> list[tuple[MovaMovieCharacter, MovaMovie]]:
        factory = get_session_factory()
        async with factory() as session:
            if await self._get_actor(session, actor_id) is None:
                raise MovieCharactersRepositoryError(
                    f"인물 ID {actor_id}를 찾을 수 없습니다.",
                    status_code=404,
                )
            result = await session.execute(
                select(MovaMovieCharacter, MovaMovie)
                .join(MovaMovie, MovaMovieCharacter.movie_id == MovaMovie.id)
                .where(MovaMovieCharacter.actor_id == actor_id)
                .order_by(MovaMovie.title.asc())
                .limit(limit),
            )
            return [(row[0], row[1]) for row in result.all()]
