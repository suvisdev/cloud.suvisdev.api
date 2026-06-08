from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.adapter.inbound.api.schemas.crew_smith_captain_schema import SmithCaptainSchema
from titanic.app.dtos.crew_smith_captain_dto import SmithCaptainResponse


class SmithCaptainUseCase(ABC):
    """smith_captain input port."""

    @abstractmethod
    async def introduce_myself(self, schemas: SmithCaptainSchema)->SmithCaptainResponse:
        pass
