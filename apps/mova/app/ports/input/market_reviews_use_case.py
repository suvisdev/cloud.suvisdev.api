from __future__ import annotations
from abc import ABC, abstractmethod

from mova.adapter.inbound.api.schemas.market_reviews_schema import MarketReviewsSchema
from mova.app.dtos.market_reviews_dto import MarketReviewsResponse


class MarketReviewsUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schemas: MarketReviewsSchema) -> MarketReviewsResponse:
        pass
