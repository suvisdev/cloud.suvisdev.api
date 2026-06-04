from __future__ import annotations

from abc import ABC, abstractmethod

from mova.adapter.outbound.orm.actors_orm import MovaActor
from mova.adapter.outbound.orm.characters_orm import MovaCharacter
from mova.adapter.outbound.orm.movies_orm import MovaMovie


class CharactersRepository(ABC):
    """영화–인물 연결(characters) 아웃바운드 포트."""

    @abstractmethod
    async def link(self, movie_id: int, actor_id: int) -> MovaCharacter:
        pass

    @abstractmethod
    async def unlink(self, link_id: int) -> bool:
        pass

    @abstractmethod
    async def list_links(
        self,
        *,
        movie_id: int | None = None,
        actor_id: int | None = None,
        limit: int = 100,
    ) -> list[MovaCharacter]:
        pass

    @abstractmethod
    async def list_actors_by_movie(
        self,
        movie_id: int,
        limit: int = 100,
    ) -> list[tuple[MovaCharacter, MovaActor]]:
        pass

    @abstractmethod
    async def list_movies_by_actor(
        self,
        actor_id: int,
        limit: int = 100,
    ) -> list[tuple[MovaCharacter, MovaMovie]]:
        pass
