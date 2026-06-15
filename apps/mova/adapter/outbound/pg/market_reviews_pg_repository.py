from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from mova.app.dtos.market_reviews_dto import MarketReviewsQuery, MarketReviewsResponse
from mova.app.ports.output.market_reviews_repository import MarketReviewsRepository

logger = logging.getLogger(__name__)


class MarketReviewsPgRepository(MarketReviewsRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def introduce_myself(self, query: MarketReviewsQuery) -> MarketReviewsResponse:
        logger.info("[MarketReviewsPgRepository] introduce_myself | query=%s", query)
        return MarketReviewsResponse(id=query.id * 10000, name=query.name + "가 레포지토리에 다녀옴")
