from __future__ import annotations

from mova.adapter.inbound.api.schemas.characters_schema import CharacterLinkCreateSchema
from mova.app.dtos.characters_dto import (
    CharacterLinkCommand,
    CharacterLinkDto,
    CharacterWithActorDto,
    CharacterWithMovieDto,
)
from mova.app.ports.input.characters_use_case import CharactersUseCase
from mova.app.ports.output.characters_repository import CharactersRepository


class CharactersInteractor(CharactersUseCase):
    def __init__(self, repository: CharactersRepository) -> None:
        self._repository = repository

    async def link(self, payload: CharacterLinkCreateSchema) -> CharacterLinkDto:
        command = CharacterLinkCommand.from_schema(payload)
        row = await self._repository.link(command)
        return CharacterLinkDto.from_orm(row)

    async def unlink(self, link_id: int) -> None:
        await self._repository.unlink(link_id)

    async def list_links(
        self,
        *,
        movie_id: int | None = None,
        actor_id: int | None = None,
        limit: int = 100,
    ) -> list[CharacterLinkDto]:
        rows = await self._repository.list_links(
            movie_id=movie_id,
            actor_id=actor_id,
            limit=limit,
        )
        return [CharacterLinkDto.from_orm(row) for row in rows]

    async def list_actors_by_movie(
        self,
        movie_id: int,
        limit: int = 100,
    ) -> list[CharacterWithActorDto]:
        rows = await self._repository.list_actors_by_movie(movie_id, limit=limit)
        return [
            CharacterWithActorDto.from_rows(link, actor)
            for link, actor in rows
        ]

    async def list_movies_by_actor(
        self,
        actor_id: int,
        limit: int = 100,
    ) -> list[CharacterWithMovieDto]:
        rows = await self._repository.list_movies_by_actor(actor_id, limit=limit)
        return [
            CharacterWithMovieDto.from_rows(link, movie)
            for link, movie in rows
        ]
