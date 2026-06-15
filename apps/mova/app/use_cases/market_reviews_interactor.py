from __future__ import annotations

from mova.adapter.inbound.api.schemas.market_reviews_schema import MarketReviewsSchema
from mova.app.dtos.market_reviews_dto import MarketReviewsQuery, MarketReviewsResponse
from mova.app.ports.input.market_reviews_use_case import MarketReviewsUseCase
from mova.app.ports.output.market_reviews_repository import MarketReviewsRepository


class MarketReviewsInteractor(MarketReviewsUseCase):
    def __init__(self, repository: MarketReviewsRepository) -> None:
        self._repository = repository

    async def introduce_myself(self, schemas: MarketReviewsSchema) -> MarketReviewsResponse:
        return await self._repository.introduce_myself(MarketReviewsQuery(
            id=schemas.id,
            name=schemas.name,
        ))
