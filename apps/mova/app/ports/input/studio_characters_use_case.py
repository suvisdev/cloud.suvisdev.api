from __future__ import annotations
from abc import ABC, abstractmethod

from mova.adapter.inbound.api.schemas.studio_characters_schema import StudioCharactersSchema
from mova.app.dtos.studio_characters_dto import StudioCharactersResponse


class StudioCharactersUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schemas: StudioCharactersSchema) -> StudioCharactersResponse:
        pass
