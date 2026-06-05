from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from mova.adapter.inbound.api.schemas.search_schema import MovaSearchItemSchema
from mova.app.ports.input.search_use_case import SearchUseCase
from mova.dependencies.search import get_search_use_case

search_router = APIRouter(tags=["mova-search"])


@search_router.get("/search", response_model=list[MovaSearchItemSchema])
async def search(
    q: str = "",
    limit: int = 12,
    search: SearchUseCase = Depends(get_search_use_case),
) -> list[MovaSearchItemSchema]:
    query = q.strip()
    if not query:
        return []
    capped = min(max(limit, 1), 50)
    try:
        return await search.search(query, limit=capped)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
