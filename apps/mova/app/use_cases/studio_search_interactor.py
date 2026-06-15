from __future__ import annotations

from mova.adapter.inbound.api.schemas.studio_search_schema import StudioSearchSchema
from mova.app.dtos.studio_search_dto import StudioSearchQuery, StudioSearchResponse
from mova.app.ports.input.studio_search_use_case import StudioSearchUseCase
from mova.app.ports.output.studio_search_repository import StudioSearchRepository


class StudioSearchInteractor(StudioSearchUseCase):
    def __init__(self, repository: StudioSearchRepository) -> None:
        self._repository = repository

    async def introduce_myself(self, schemas: StudioSearchSchema) -> StudioSearchResponse:
        return await self._repository.introduce_myself(StudioSearchQuery(
            id=schemas.id,
            name=schemas.name,
        ))
