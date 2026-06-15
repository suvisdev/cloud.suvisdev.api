from __future__ import annotations

from abc import ABC, abstractmethod

from mova.app.dtos.studio_movies_dto import StudioMoviesQuery, StudioMoviesResponse


class StudioMoviesRepository(ABC):

    @abstractmethod
    async def introduce_myself(self, query: StudioMoviesQuery) -> StudioMoviesResponse:
        pass
