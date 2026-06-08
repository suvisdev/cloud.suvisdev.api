from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.adapter.inbound.api.schemas.crew_hartley_violin_schema import HartleyViolinSchema
from titanic.app.dtos.crew_hartley_violin_dto import HartleyViolinResponse

class HartleyViolinUseCase(ABC):
    """crew_hartley_violin input port."""

    @abstractmethod
    async def introduce_myself(self, schemas: HartleyViolinSchema)->HartleyViolinResponse:
        pass
