from __future__ import annotations

from mova.adapter.inbound.api.schemas.studio_characters_schema import StudioCharactersSchema
from mova.app.dtos.studio_characters_dto import StudioCharactersQuery, StudioCharactersResponse
from mova.app.ports.input.studio_characters_use_case import StudioCharactersUseCase
from mova.app.ports.output.studio_characters_repository import StudioCharactersRepository


class StudioCharactersInteractor(StudioCharactersUseCase):
    def __init__(self, repository: StudioCharactersRepository) -> None:
        self._repository = repository

    async def introduce_myself(self, schemas: StudioCharactersSchema) -> StudioCharactersResponse:
        return await self._repository.introduce_myself(StudioCharactersQuery(
            id=schemas.id,
            name=schemas.name,
        ))
