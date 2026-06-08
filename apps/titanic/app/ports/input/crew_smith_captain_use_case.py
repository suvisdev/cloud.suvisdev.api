from __future__ import annotations

from abc import ABC, abstractmethod
from titanic.adapter.inbound.api.schemas.crew_smith_captain_schema import SmithCaptainSchema


class SmithCaptainUseCase(ABC):
    """smith_captain input port."""

    @abstractmethod
    async def introduce_myself(self, schemas: list["SmithCaptainSchema"]):
        pass
