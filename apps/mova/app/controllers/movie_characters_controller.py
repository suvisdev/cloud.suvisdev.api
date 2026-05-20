import logging

from mova.app.schemas.movie_characters_schema import (
    MovieCharacterLinkCreateSchema,
    MovieCharacterLinkSchema,
    MovieCharacterWithActorSchema,
    MovieCharacterWithMovieSchema,
)
from mova.app.services.movie_characters_service import MovieCharactersService

logger = logging.getLogger(__name__)


class MovieCharactersController:
    def __init__(self) -> None:
        self.service = MovieCharactersService()

    async def link(self, payload: MovieCharacterLinkCreateSchema) -> MovieCharacterLinkSchema:
        logger.info(
            "[MovieCharactersController] link — movie_id=%s actor_id=%s",
            payload.movie_id,
            payload.actor_id,
        )
        return await self.service.link(payload)

    async def unlink(self, link_id: int) -> None:
        logger.info("[MovieCharactersController] unlink — id=%s", link_id)
        await self.service.unlink(link_id)

    async def list_links(
        self,
        *,
        movie_id: int | None = None,
        actor_id: int | None = None,
        limit: int = 100,
    ) -> list[MovieCharacterLinkSchema]:
        return await self.service.list_links(
            movie_id=movie_id,
            actor_id=actor_id,
            limit=limit,
        )

    async def list_actors_by_movie(
        self,
        movie_id: int,
        limit: int = 100,
    ) -> list[MovieCharacterWithActorSchema]:
        return await self.service.list_actors_by_movie(movie_id, limit=limit)

    async def list_movies_by_actor(
        self,
        actor_id: int,
        limit: int = 100,
    ) -> list[MovieCharacterWithMovieSchema]:
        return await self.service.list_movies_by_actor(actor_id, limit=limit)
