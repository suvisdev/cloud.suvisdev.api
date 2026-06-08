from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.adapter.inbound.api.schemas.crew_walter_roaster_schema import WalterSchema

class WalterUseCase(ABC):
    """roaster input port."""

    @abstractmethod
    async def introduce_myself(self, schemas: list["WalterSchema"]):
        pass
