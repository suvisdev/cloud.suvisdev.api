from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from mova.app.dtos.market_picks_dto import MarketPicksQuery, MarketPicksResponse
from mova.app.ports.output.market_picks_repository import MarketPicksRepository

logger = logging.getLogger(__name__)


class MarketPicksPgRepository(MarketPicksRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def introduce_myself(self, query: MarketPicksQuery) -> MarketPicksResponse:
        logger.info("[MarketPicksPgRepository] introduce_myself | query=%s", query)
        return MarketPicksResponse(id=query.id * 10000, name=query.name + "가 레포지토리에 다녀옴")
