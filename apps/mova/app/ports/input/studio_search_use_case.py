from __future__ import annotations
from abc import ABC, abstractmethod

from mova.adapter.inbound.api.schemas.studio_search_schema import StudioSearchSchema
from mova.app.dtos.studio_search_dto import StudioSearchResponse


class StudioSearchUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schemas: StudioSearchSchema) -> StudioSearchResponse:
        pass
