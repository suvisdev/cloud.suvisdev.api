from __future__ import annotations

from typing import Any

from mova.adapter.inbound.api.schemas.search_schema import MovaSearchItemSchema
from mova.domain.value_objects.movie_catalog import resolve_canonical_slug
from mova.app.ports.input.search_use_case import SearchUseCase
from mova.app.ports.output.search_repository import SearchHit, SearchRepository


class SearchInteractor(SearchUseCase):
    def __init__(self, repository: SearchRepository) -> None:
        self._repository = repository

    def _to_item(self, hit: SearchHit) -> MovaSearchItemSchema:
        movie = hit.movie
        return MovaSearchItemSchema(
            id=resolve_canonical_slug(movie.slug, title=movie.title),
            title=movie.title,
            year=movie.release_year or "",
            rating=float(movie.rating or 0),
            poster=movie.poster_url or "",
            match_type=hit.match_type,
        )

    async def search(self, query: str, *, limit: int = 12) -> list[MovaSearchItemSchema]:
        q = query.strip()
        if not q:
            return []
        hits = await self._repository.search(q, limit=limit)
        return [self._to_item(hit) for hit in hits]

    async def search_by_intent(
        self,
        *,
        refined_query: str,
        keywords: list[str],
        intent_type: str,
        search_filters: dict[str, Any] | None,
        limit: int = 12,
    ) -> list[MovaSearchItemSchema]:
        filters = search_filters if isinstance(search_filters, dict) else {}
        structured = await self._repository.search_by_filters(
            filters,
            intent_type=intent_type or "mood",
            limit=limit,
        )
        if structured:
            return [self._to_item(hit) for hit in structured]

        seen: set[str] = set()
        out: list[MovaSearchItemSchema] = []
        queries: list[str] = []
        if refined_query.strip():
            queries.append(refined_query.strip())
        for keyword in keywords:
            key = keyword.strip()
            if key and key not in queries:
                queries.append(key)
        for q in queries[:limit]:
            for item in await self.search(q, limit=8):
                if item.id in seen:
                    continue
                seen.add(item.id)
                out.append(item)
                if len(out) >= limit:
                    return out
        return out
