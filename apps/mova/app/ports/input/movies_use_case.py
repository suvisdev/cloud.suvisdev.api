from __future__ import annotations

from abc import ABC, abstractmethod

from mova.adapter.inbound.api.schemas.search_schema import MovaTitleDetailSchema
from mova.adapter.inbound.api.schemas.movies_schema import (
    MovieCreateSchema,
    MovieSchema,
    MovieTitleCreateSchema,
    MovieTitleSchema,
)


class MoviesUseCase(ABC):
    """영화(movies) 입력 포트."""

    @abstractmethod
    async def save_movie(self, payload: MovieCreateSchema) -> MovieSchema:
        pass

    @abstractmethod
    async def save_title(self, payload: MovieTitleCreateSchema) -> MovieTitleSchema:
        pass

    @abstractmethod
    async def list_movies(self, limit: int = 100) -> list[MovieSchema]:
        pass

    @abstractmethod
    async def list_titles(self, limit: int = 100) -> list[MovieTitleSchema]:
        pass

    @abstractmethod
    async def get_movie(self, movie_id: int) -> MovieSchema:
        pass

    @abstractmethod
    async def get_title_by_slug(self, slug: str) -> MovaTitleDetailSchema:
        pass
