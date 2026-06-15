from __future__ import annotations

from mova.adapter.inbound.api.schemas.studio_tags_schema import StudioTagsSchema
from mova.app.dtos.studio_tags_dto import StudioTagsQuery, StudioTagsResponse
from mova.app.ports.input.studio_tags_use_case import StudioTagsUseCase
from mova.app.ports.output.studio_tags_repository import StudioTagsRepository


class StudioTagsInteractor(StudioTagsUseCase):
    def __init__(self, repository: StudioTagsRepository) -> None:
        self._repository = repository

    async def introduce_myself(self, schemas: StudioTagsSchema) -> StudioTagsResponse:
        return await self._repository.introduce_myself(StudioTagsQuery(
            id=schemas.id,
            name=schemas.name,
        ))
