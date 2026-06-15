from __future__ import annotations
from abc import ABC, abstractmethod

from mova.adapter.inbound.api.schemas.platform_assistants_schema import PlatformAssistantsSchema
from mova.app.dtos.platform_assistants_dto import PlatformAssistantsResponse


class PlatformAssistantsUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schemas: PlatformAssistantsSchema) -> PlatformAssistantsResponse:
        pass
