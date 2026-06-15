from fastapi import APIRouter, Depends

from mova.adapter.inbound.api.schemas.market_rankings_schema import MarketRankingsSchema
from mova.app.dtos.market_rankings_dto import MarketRankingsResponse
from mova.app.ports.input.market_rankings_use_case import MarketRankingsUseCase
from mova.dependencies.market_rankings_provider import get_market_rankings_use_case

market_rankings_router = APIRouter(prefix="/rankings", tags=["mova-rankings"])


@market_rankings_router.get("/myself")
async def introduce_myself(
    rankings: MarketRankingsUseCase = Depends(get_market_rankings_use_case),
) -> MarketRankingsResponse:
    return await rankings.introduce_myself(
        MarketRankingsSchema(id=1, name="프로듀서 (Producer)")
    )
