from __future__ import annotations
from abc import ABC, abstractmethod

from mova.adapter.inbound.api.schemas.studio_tags_schema import StudioTagsSchema
from mova.app.dtos.studio_tags_dto import StudioTagsResponse


class StudioTagsUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schemas: StudioTagsSchema) -> StudioTagsResponse:
        pass
