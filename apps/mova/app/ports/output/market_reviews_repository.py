from __future__ import annotations

from abc import ABC, abstractmethod

from mova.app.dtos.market_reviews_dto import MarketReviewsQuery, MarketReviewsResponse


class MarketReviewsRepository(ABC):

    @abstractmethod
    async def introduce_myself(self, query: MarketReviewsQuery) -> MarketReviewsResponse:
        pass
