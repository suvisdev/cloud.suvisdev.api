import logging

from mova.app.repositories.characters_repository import CharactersRepository
from mova.app.schemas.characters_schema import (
    CharacterLinkCreateSchema,
    CharacterLinkSchema,
    CharacterWithActorSchema,
    CharacterWithMovieSchema,
)

logger = logging.getLogger(__name__)


class CharactersService:
    def __init__(self) -> None:
        self.repository = CharactersRepository()

    def _to_link_schema(self, row) -> CharacterLinkSchema:
        return CharacterLinkSchema(
            id=row.id,
            movie_id=row.movie_id,
            actor_id=row.actor_id,
        )

    async def link(self, payload: CharacterLinkCreateSchema) -> CharacterLinkSchema:
        logger.info(
            "[CharactersService] link — movie_id=%s actor_id=%s",
            payload.movie_id,
            payload.actor_id,
        )
        row = await self.repository.link(payload.movie_id, payload.actor_id)
        return self._to_link_schema(row)

    async def unlink(self, link_id: int) -> None:
        await self.repository.unlink(link_id)

    async def list_links(
        self,
        *,
        movie_id: int | None = None,
        actor_id: int | None = None,
        limit: int = 100,
    ) -> list[CharacterLinkSchema]:
        rows = await self.repository.list_links(
            movie_id=movie_id,
            actor_id=actor_id,
            limit=limit,
        )
        return [self._to_link_schema(r) for r in rows]

    async def list_actors_by_movie(
        self,
        movie_id: int,
        limit: int = 100,
    ) -> list[CharacterWithActorSchema]:
        rows = await self.repository.list_actors_by_movie(movie_id, limit=limit)
        return [
            CharacterWithActorSchema(
                id=link.id,
                movie_id=link.movie_id,
                actor_id=link.actor_id,
                actor_name=actor.name,
                role_type=actor.role_type,
                profile_photo=actor.profile_photo_url,
            )
            for link, actor in rows
        ]

    async def list_movies_by_actor(
        self,
        actor_id: int,
        limit: int = 100,
    ) -> list[CharacterWithMovieSchema]:
        rows = await self.repository.list_movies_by_actor(actor_id, limit=limit)
        return [
            CharacterWithMovieSchema(
                id=link.id,
                movie_id=link.movie_id,
                actor_id=link.actor_id,
                slug=movie.slug,
                movie_title=movie.title,
                release_year=movie.release_year,
                rating=movie.rating,
                poster=movie.poster_url,
                platform=movie.platform,
            )
            for link, movie in rows
        ]
