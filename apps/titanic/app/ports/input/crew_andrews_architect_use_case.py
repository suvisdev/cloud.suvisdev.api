from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.adapter.inbound.api.schemas.crew_andrews_architect_schema import AndrewsArchitectSchema
from titanic.app.dtos.crew_andrews_architect_dto import AndrewsArchitectResponse


class AndrewsArchitectUseCase(ABC):
    """AndrewsArchitect input port."""

    @abstractmethod
    async def introduce_myself(
        self,
        schemas: AndrewsArchitectSchema,
    )->AndrewsArchitectResponse:
        pass
