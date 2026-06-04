from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from mova.adapter.inbound.api.schemas.search_schema import MovaSearchItemSchema
from mova.app.ports.input.search_use_case import SearchUseCase
from mova.app.use_cases.search_interactor import SearchInteractor

search_router = APIRouter(tags=["mova-search"])

logger = logging.getLogger(__name__)


@search_router.get("/search", response_model=list[MovaSearchItemSchema])
async def search(q: str = "", limit: int = 12) -> list[MovaSearchItemSchema]:
    query = q.strip()
    if not query:
        return []
    capped = min(max(limit, 1), 50)
    use_case: SearchUseCase = SearchInteractor()
    try:
        return await use_case.search(query, limit=capped)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
