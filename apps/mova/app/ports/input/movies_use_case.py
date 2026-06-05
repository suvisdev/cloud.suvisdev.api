from __future__ import annotations

from abc import ABC, abstractmethod

from mova.adapter.inbound.api.schemas.movies_schema import MovieCreateSchema, MovieTitleCreateSchema
from mova.app.dtos.movies_dto import MovieDto, MovieTitleDto, TitleDetailDto


class MoviesUseCase(ABC):
    """영화(movies) 입력 포트."""

    @abstractmethod
    async def save_movie(self, payload: MovieCreateSchema) -> MovieDto:
        pass

    @abstractmethod
    async def save_title(self, payload: MovieTitleCreateSchema) -> MovieTitleDto:
        pass

    @abstractmethod
    async def list_movies(self, limit: int = 100) -> list[MovieDto]:
        pass

    @abstractmethod
    async def list_titles(self, limit: int = 100) -> list[MovieTitleDto]:
        pass

    @abstractmethod
    async def get_movie(self, movie_id: int) -> MovieDto:
        pass

    @abstractmethod
    async def get_title_by_slug(self, slug: str) -> TitleDetailDto:
        pass
