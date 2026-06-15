from __future__ import annotations

from abc import ABC, abstractmethod

from mova.app.dtos.market_picks_dto import MarketPicksQuery, MarketPicksResponse


class MarketPicksRepository(ABC):

    @abstractmethod
    async def introduce_myself(self, query: MarketPicksQuery) -> MarketPicksResponse:
        pass
