from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.adapter.inbound.api.schemas.crew_walter_roaster_schema import WalterSchema
from titanic.app.dtos.crew_walter_roaster_dto import WalterResponse


class WalterUseCase(ABC):
    """Walter 소개(GET) 입력 포트 (ABC)."""

    @abstractmethod
    async def introduce_myself(self, payload: WalterSchema) -> WalterResponse:
        pass
