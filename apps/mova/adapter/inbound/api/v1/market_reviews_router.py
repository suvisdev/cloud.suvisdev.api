from fastapi import APIRouter, Depends

from mova.adapter.inbound.api.schemas.market_reviews_schema import MarketReviewsSchema
from mova.app.dtos.market_reviews_dto import MarketReviewsResponse
from mova.app.ports.input.market_reviews_use_case import MarketReviewsUseCase
from mova.dependencies.market_reviews_provider import get_market_reviews_use_case

market_reviews_router = APIRouter(prefix="/reviews", tags=["mova-reviews"])


@market_reviews_router.get("/myself")
async def introduce_myself(
    reviews: MarketReviewsUseCase = Depends(get_market_reviews_use_case),
) -> MarketReviewsResponse:
    return await reviews.introduce_myself(
        MarketReviewsSchema(id=1, name="평론가 (Critic)")
    )
