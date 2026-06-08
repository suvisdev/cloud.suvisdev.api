from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.adapter.inbound.api.schemas.crew_hartley_violin_schema import HartleyViolinSchema

class HartleyViolinUseCase(ABC):
    """crew_hartley_violin input port."""

    @abstractmethod
    async def introduce_myself(self, schemas: list["HartleyViolinSchema"]):
        pass
