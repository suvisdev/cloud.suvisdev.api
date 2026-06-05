from __future__ import annotations

from abc import ABC, abstractmethod

from mova.adapter.inbound.api.schemas.characters_schema import CharacterLinkCreateSchema
from mova.app.dtos.characters_dto import (
    CharacterLinkDto,
    CharacterWithActorDto,
    CharacterWithMovieDto,
)


class CharactersUseCase(ABC):
    """영화–인물 연결(characters) 입력 포트."""

    @abstractmethod
    async def link(self, payload: CharacterLinkCreateSchema) -> CharacterLinkDto:
        pass

    @abstractmethod
    async def unlink(self, link_id: int) -> None:
        pass

    @abstractmethod
    async def list_links(
        self,
        *,
        movie_id: int | None = None,
        actor_id: int | None = None,
        limit: int = 100,
    ) -> list[CharacterLinkDto]:
        pass

    @abstractmethod
    async def list_actors_by_movie(
        self,
        movie_id: int,
        limit: int = 100,
    ) -> list[CharacterWithActorDto]:
        pass

    @abstractmethod
    async def list_movies_by_actor(
        self,
        actor_id: int,
        limit: int = 100,
    ) -> list[CharacterWithMovieDto]:
        pass
