from __future__ import annotations

from fastapi import APIRouter, Depends

from mova.adapter.inbound.api.http_errors import invoke
from mova.adapter.inbound.api.schemas.rankings_schema import HotRankingDisplaySchema
from mova.adapter.outbound.pg.rankings_pg_repository import RankingsRepositoryError
from mova.domain.value_objects.ranking_source import DEFAULT_HOT_RANKING_SOURCE
from mova.app.ports.input.rankings_use_case import RankingsUseCase
from mova.dependencies.rankings import get_rankings_use_case

rankings_router = APIRouter(tags=["mova-rankings"])


@rankings_router.get("/rankings/hot", response_model=list[HotRankingDisplaySchema])
async def list_hot_rankings(
    limit: int = 20,
    ranked_at: str | None = None,
    source: str = DEFAULT_HOT_RANKING_SOURCE,
    rankings: RankingsUseCase = Depends(get_rankings_use_case),
) -> list[HotRankingDisplaySchema]:
    """Mova HOT 랭킹 — 기본 `source=chat_trend` (채팅·추천 집계)."""
    rows = await invoke(
        rankings.list_hot_rankings_from_query(
            source=source,
            ranked_at=ranked_at,
            limit=limit,
        ),
        domain_errors=(RankingsRepositoryError,),
    )
    return [row.to_schema() for row in rows]


@rankings_router.post("/rankings/hot/refresh", response_model=list[HotRankingDisplaySchema])
async def refresh_chat_trend_rankings(
    window_days: int = 7,
    limit: int = 10,
    rankings: RankingsUseCase = Depends(get_rankings_use_case),
) -> list[HotRankingDisplaySchema]:
    """chat·picks 집계로 `source=chat_trend` 랭킹 스냅샷 갱신."""
    rows = await invoke(
        rankings.refresh_chat_trend_rankings(window_days=window_days, limit=limit),
        domain_errors=(RankingsRepositoryError,),
    )
    return [row.to_schema() for row in rows]
