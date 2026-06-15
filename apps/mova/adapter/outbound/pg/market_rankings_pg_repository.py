from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from mova.app.dtos.market_rankings_dto import MarketRankingsQuery, MarketRankingsResponse
from mova.app.ports.output.market_rankings_repository import MarketRankingsRepository

logger = logging.getLogger(__name__)


class MarketRankingsPgRepository(MarketRankingsRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def introduce_myself(self, query: MarketRankingsQuery) -> MarketRankingsResponse:
        logger.info("[MarketRankingsPgRepository] introduce_myself | query=%s", query)
        return MarketRankingsResponse(id=query.id * 10000, name=query.name + "가 레포지토리에 다녀옴")
