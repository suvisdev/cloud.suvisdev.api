from __future__ import annotations

from abc import ABC, abstractmethod
from titanic.adapter.inbound.api.schemas.crew_lowe_boat_schema import LoweBoatSchema


class LoweBoatUseCase(ABC):
    """crew_lowe_boat input port."""

    @abstractmethod
    async def introduce_myself(self, schemas: list["LoweBoatSchema"]):
        pass
