from __future__ import annotations

from abc import ABC, abstractmethod

from mova.adapter.outbound.orm.movies_orm import MovaMovie
from mova.adapter.outbound.orm.tags_orm import MovaTag
from mova.app.dtos.tags_dto import TagAttachCommand


class TagsRepository(ABC):
    """영화 태그(tags) 아웃바운드 포트."""

    @abstractmethod
    async def attach(self, command: TagAttachCommand) -> MovaTag:
        pass

    @abstractmethod
    async def list_catalog(self, limit: int = 100) -> list[MovaTag]:
        pass

    @abstractmethod
    async def list_by_movie(self, movie_id: int, limit: int = 50) -> list[MovaTag]:
        pass

    @abstractmethod
    async def list_movies_by_slug(
        self,
        slug: str,
        limit: int = 50,
    ) -> list[tuple[MovaTag, MovaMovie]]:
        pass

    @abstractmethod
    async def unlink(self, link_id: int) -> None:
        pass
