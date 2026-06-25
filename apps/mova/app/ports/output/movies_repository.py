"""영화 Output Port — PgRepository가 구현한다."""

from __future__ import annotations

from abc import ABC, abstractmethod

from mova.app.dtos.studio_import_dto import StudioImportQuery, StudioImportResponse
from mova.app.dtos.studio_movies_dto import MovieDetailDto, MovieFilterQuery, MovieListDto


class MoviesRepositoryPort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: StudioImportQuery) -> StudioImportResponse:
        """Import 담당자 소개 정보 반환."""

    @abstractmethod
    async def get_by_slug(self, slug: str) -> MovieDetailDto | None:
        """slug로 영화 상세 (출연진·태그 포함) 조회."""

    @abstractmethod
    async def list_movies(self, query: MovieFilterQuery) -> MovieListDto:
        """장르·연도·평점·연령등급·플랫폼 필터 + 정렬 + 페이지네이션."""
