"""랭킹 라우터 — GET /mova/rankings/hot"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from mova.adapter.inbound.api.schemas.market_rankings_schema import HotRankingListSchema
from mova.app.ports.input.market_rankings_use_case import RankingsUseCase
from mova.dependencies.market_rankings_provider import get_rankings_use_case

market_rankings_router = APIRouter(prefix="/rankings", tags=["mova-rankings"])


class _MyselfResponse(BaseModel):
    id: int
    name: str


@market_rankings_router.get("/myself", response_model=_MyselfResponse)
async def introduce_myself() -> _MyselfResponse:
    return _MyselfResponse(id=1, name="프로듀서 (Producer)")


@market_rankings_router.get("/hot", response_model=HotRankingListSchema)
async def get_hot_rankings(
    source: str = Query("chat_trend", description="chat_trend | box_office | manual"),
    limit: int = Query(10, ge=1, le=50),
    use_case: RankingsUseCase = Depends(get_rankings_use_case),
) -> HotRankingListSchema:
    """HOT 랭킹 조회 (source 별 최신 스냅샷)."""
    dto = await use_case.get_hot(source, limit)
    return dto.to_schema()
