from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.adapter.inbound.api.schemas.crew_walter_roaster_schema import WalterSchema
from titanic.app.dtos.crew_walter_roaster_dto import WalterResponse

class WalterUseCase(ABC):
    """roaster input port."""

    @abstractmethod
    async def introduce_myself(self, schemas: WalterSchema)->WalterResponse:
        pass
