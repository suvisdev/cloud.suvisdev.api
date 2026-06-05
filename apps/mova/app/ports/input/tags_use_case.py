from __future__ import annotations

from abc import ABC, abstractmethod

from mova.adapter.inbound.api.schemas.tags_schema import TagCreateSchema
from mova.app.dtos.tags_dto import MovieByTagDto, TagCatalogDto, TagDto


class TagsUseCase(ABC):
    """영화 태그(tags) 입력 포트."""

    @abstractmethod
    async def attach(self, payload: TagCreateSchema) -> TagDto:
        pass

    @abstractmethod
    async def list_catalog(self, limit: int = 100) -> list[TagCatalogDto]:
        pass

    @abstractmethod
    async def list_by_movie(self, movie_id: int, limit: int = 50) -> list[TagDto]:
        pass

    @abstractmethod
    async def list_movies_by_slug(self, slug: str, limit: int = 50) -> list[MovieByTagDto]:
        pass

    @abstractmethod
    async def unlink(self, link_id: int) -> None:
        pass
