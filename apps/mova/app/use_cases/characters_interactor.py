from __future__ import annotations

import logging

from mova.adapter.inbound.api.schemas.characters_schema import (
    CharacterLinkCreateSchema,
    CharacterLinkSchema,
    CharacterWithActorSchema,
    CharacterWithMovieSchema,
)
from mova.adapter.outbound.pg.characters_pg_repository import CharactersPgRepository
from mova.app.ports.input.characters_use_case import CharactersUseCase
from mova.app.ports.output.characters_repository import CharactersRepository

logger = logging.getLogger(__name__)


class CharactersInteractor(CharactersUseCase):
    def __init__(self) -> None:
        self._repository: CharactersRepository = CharactersPgRepository()

    def _to_link_schema(self, row) -> CharacterLinkSchema:
        return CharacterLinkSchema(
            id=row.id,
            movie_id=row.movie_id,
            actor_id=row.actor_id,
        )

    async def link(self, payload: CharacterLinkCreateSchema) -> CharacterLinkSchema:
        logger.info(
            "[CharactersInteractor] link — movie_id=%s actor_id=%s",
            payload.movie_id,
            payload.actor_id,
        )
        row = await self._repository.link(payload.movie_id, payload.actor_id)
        return self._to_link_schema(row)

    async def unlink(self, link_id: int) -> None:
        await self._repository.unlink(link_id)

    async def list_links(
        self,
        *,
        movie_id: int | None = None,
        actor_id: int | None = None,
        limit: int = 100,
    ) -> list[CharacterLinkSchema]:
        rows = await self._repository.list_links(
            movie_id=movie_id,
            actor_id=actor_id,
            limit=limit,
        )
        return [self._to_link_schema(row) for row in rows]

    async def list_actors_by_movie(
        self,
        movie_id: int,
        limit: int = 100,
    ) -> list[CharacterWithActorSchema]:
        rows = await self._repository.list_actors_by_movie(movie_id, limit=limit)
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
        rows = await self._repository.list_movies_by_actor(actor_id, limit=limit)
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
