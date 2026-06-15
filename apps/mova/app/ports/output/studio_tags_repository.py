from __future__ import annotations

from abc import ABC, abstractmethod

from mova.app.dtos.studio_tags_dto import StudioTagsQuery, StudioTagsResponse


class StudioTagsRepository(ABC):

    @abstractmethod
    async def introduce_myself(self, query: StudioTagsQuery) -> StudioTagsResponse:
        pass
