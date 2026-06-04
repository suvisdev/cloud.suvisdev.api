from __future__ import annotations

import logging
from datetime import date as date_type

from fastapi import APIRouter, HTTPException

from mova.adapter.inbound.api.schemas.rankings_schema import HotRankingDisplaySchema
from mova.adapter.outbound.pg.rankings_pg_repository import RankingsRepositoryError
from mova.app.ports.input.rankings_use_case import RankingsUseCase
from mova.app.use_cases.rankings_interactor import RankingsInteractor

rankings_router = APIRouter(tags=["mova-rankings"])

logger = logging.getLogger(__name__)


@rankings_router.get("/rankings/hot", response_model=list[HotRankingDisplaySchema])
async def list_hot_rankings(
    limit: int = 20,
    ranked_at: str | None = None,
) -> list[HotRankingDisplaySchema]:
    """Mova HOT 랭킹 (선택 쿼리 ranked_at=YYYY-MM-DD)."""
    parsed_date = None
    if ranked_at:
        try:
            parsed_date = date_type.fromisoformat(ranked_at)
        except ValueError as e:
            raise HTTPException(status_code=400, detail="ranked_at 형식은 YYYY-MM-DD 입니다.") from e
    use_case: RankingsUseCase = RankingsInteractor()
    try:
        return await use_case.list_hot_rankings(ranked_at=parsed_date, limit=limit)
    except RankingsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
