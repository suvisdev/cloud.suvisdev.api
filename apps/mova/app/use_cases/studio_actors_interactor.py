from __future__ import annotations

from mova.adapter.inbound.api.schemas.studio_actors_schema import StudioActorsSchema
from mova.app.dtos.studio_actors_dto import StudioActorsQuery, StudioActorsResponse
from mova.app.ports.input.studio_actors_use_case import StudioActorsUseCase
from mova.app.ports.output.studio_actors_repository import StudioActorsRepository


class StudioActorsInteractor(StudioActorsUseCase):
    def __init__(self, repository: StudioActorsRepository) -> None:
        self._repository = repository

    async def introduce_myself(self, schemas: StudioActorsSchema) -> StudioActorsResponse:
        return await self._repository.introduce_myself(StudioActorsQuery(
            id=schemas.id,
            name=schemas.name,
        ))
