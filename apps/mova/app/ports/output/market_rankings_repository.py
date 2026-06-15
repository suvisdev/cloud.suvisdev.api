from __future__ import annotations

from abc import ABC, abstractmethod

from mova.app.dtos.market_rankings_dto import MarketRankingsQuery, MarketRankingsResponse


class MarketRankingsRepository(ABC):

    @abstractmethod
    async def introduce_myself(self, query: MarketRankingsQuery) -> MarketRankingsResponse:
        pass
