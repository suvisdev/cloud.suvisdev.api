from __future__ import annotations
from abc import ABC, abstractmethod

from mova.adapter.inbound.api.schemas.studio_actors_schema import StudioActorsSchema
from mova.app.dtos.studio_actors_dto import StudioActorsResponse


class StudioActorsUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schemas: StudioActorsSchema) -> StudioActorsResponse:
        pass
