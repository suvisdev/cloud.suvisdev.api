from __future__ import annotations

from abc import ABC, abstractmethod

from mova.adapter.outbound.orm.movies_orm import MovaMovie


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
    async def upsert(self, data: dict) -> MovaMovie:
        pass

    @abstractmethod
    async def upsert_title(self, title: str) -> int:
        pass

    @abstractmethod
    async def upsert_titles(self, titles: list[str]) -> list[int]:
        pass

    @abstractmethod
    async def list_movies(self, limit: int = 100) -> list[MovaMovie]:
        pass

    @abstractmethod
    async def list_titles(self, limit: int = 100) -> list[MovaMovie]:
        pass
