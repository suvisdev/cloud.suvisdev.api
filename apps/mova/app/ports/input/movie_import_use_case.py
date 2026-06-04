from __future__ import annotations

from abc import ABC, abstractmethod

from mova.adapter.inbound.api.schemas.movie_import_schema import MovieImportResultSchema


class MovieImportUseCase(ABC):
    @abstractmethod
    async def import_popular(
        self,
        *,
        pages: int = 2,
        setup_rankings: bool = True,
    ) -> MovieImportResultSchema:
        pass

    @abstractmethod
    async def import_search(
        self,
        query: str,
        *,
        pages: int = 1,
        setup_rankings: bool = False,
    ) -> MovieImportResultSchema:
        pass

    @abstractmethod
    async def import_by_tmdb_id(self, tmdb_id: int) -> MovieImportResultSchema:
        pass

    @abstractmethod
    async def import_by_kofic_cd(self, movie_cd: str) -> MovieImportResultSchema:
        pass

    @abstractmethod
    async def import_kofic_daily(
        self,
        *,
        target_date: str,
        setup_rankings: bool = True,
    ) -> MovieImportResultSchema:
        pass

    @abstractmethod
    async def import_kofic_weekly(
        self,
        *,
        target_date: str,
        week_gb: str = "0",
        setup_rankings: bool = True,
    ) -> MovieImportResultSchema:
        pass

    @abstractmethod
    async def enrich_missing_posters(self, *, limit: int = 50) -> MovieImportResultSchema:
        pass
