from __future__ import annotations

from abc import ABC, abstractmethod

from mova.app.dtos.studio_actors_dto import StudioActorsQuery, StudioActorsResponse


class StudioActorsRepository(ABC):

    @abstractmethod
    async def introduce_myself(self, query: StudioActorsQuery) -> StudioActorsResponse:
        pass
