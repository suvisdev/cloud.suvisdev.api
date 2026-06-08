from __future__ import annotations

from fastapi import APIRouter, Depends

from mova.adapter.inbound.api.http_errors import invoke
from mova.adapter.inbound.api.schemas.search_schema import MovaSearchItemSchema
from mova.app.ports.input.search_use_case import SearchUseCase
from mova.dependencies.search_provider import get_search_use_case

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
    rows = await invoke(search.search(query, limit=capped))
    return [row.to_schema() for row in rows]
