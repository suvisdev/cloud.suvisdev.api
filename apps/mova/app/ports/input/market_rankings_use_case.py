from __future__ import annotations
from abc import ABC, abstractmethod

from mova.adapter.inbound.api.schemas.market_rankings_schema import MarketRankingsSchema
from mova.app.dtos.market_rankings_dto import MarketRankingsResponse


class MarketRankingsUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schemas: MarketRankingsSchema) -> MarketRankingsResponse:
        pass
