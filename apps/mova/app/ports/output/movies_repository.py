from __future__ import annotations

from abc import ABC, abstractmethod

from mova.adapter.outbound.orm.movies_orm import MovaMovie
from mova.app.dtos.movies_dto import MovieTitleCommand, MovieUpsertCommand


class MoviesRepository(ABC):
    """영화(movies) 아웃바운드 포트."""

    @abstractmethod
    async def get_by_id(self, movie_id: int) -> MovaMovie | None:
        pass

    @abstractmethod
    async def get_by_slug(self, slug: str) -> MovaMovie | None:
        pass

    @abstractmethod
    async def find_by_title(self, title: str) -> MovaMovie | None:
        pass

    @abstractmethod
    async def upsert(self, command: MovieUpsertCommand) -> MovaMovie:
        pass

    @abstractmethod
    async def upsert_title(self, command: MovieTitleCommand) -> int:
        pass

    @abstractmethod
    async def upsert_titles(self, commands: list[MovieTitleCommand]) -> list[int]:
        pass

    @abstractmethod
    async def list_movies(self, limit: int = 100) -> list[MovaMovie]:
        pass

    @abstractmethod
    async def list_titles(self, limit: int = 100) -> list[MovaMovie]:
        pass
