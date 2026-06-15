from __future__ import annotations
from abc import ABC, abstractmethod

from mova.adapter.inbound.api.schemas.studio_movies_schema import StudioMoviesSchema
from mova.app.dtos.studio_movies_dto import StudioMoviesResponse


class StudioMoviesUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schemas: StudioMoviesSchema) -> StudioMoviesResponse:
        pass
