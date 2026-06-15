from __future__ import annotations

from mova.adapter.inbound.api.schemas.platform_assistants_schema import PlatformAssistantsSchema
from mova.app.dtos.platform_assistants_dto import PlatformAssistantsQuery, PlatformAssistantsResponse
from mova.app.ports.input.platform_assistants_use_case import PlatformAssistantsUseCase
from mova.app.ports.output.platform_assistants_repository import PlatformAssistantsRepository


class PlatformAssistantsInteractor(PlatformAssistantsUseCase):
    def __init__(self, repository: PlatformAssistantsRepository) -> None:
        self._repository = repository

    async def introduce_myself(self, schemas: PlatformAssistantsSchema) -> PlatformAssistantsResponse:
        return await self._repository.introduce_myself(PlatformAssistantsQuery(
            id=schemas.id,
            name=schemas.name,
        ))
