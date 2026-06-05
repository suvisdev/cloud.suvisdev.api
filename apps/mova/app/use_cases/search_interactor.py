from __future__ import annotations

from mova.app.dtos.search_dto import SearchIntentQuery, SearchItemDto
from mova.domain.value_objects.movie_catalog import resolve_canonical_slug
from mova.app.ports.input.search_use_case import SearchUseCase
from mova.app.ports.output.search_repository import SearchHit, SearchRepository


class SearchInteractor(SearchUseCase):
    def __init__(self, repository: SearchRepository) -> None:
        self._repository = repository

    def _to_item(self, hit: SearchHit) -> SearchItemDto:
        movie = hit.movie
        slug = resolve_canonical_slug(movie.slug, title=movie.title)
        return SearchItemDto.from_hit(hit, slug=slug)

    async def search(self, query: str, *, limit: int = 12) -> list[SearchItemDto]:
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
        search_filters: dict | None,
        limit: int = 12,
    ) -> list[SearchItemDto]:
        query = SearchIntentQuery(
            refined_query=refined_query,
            keywords=keywords,
            intent_type=intent_type or "mood",
            search_filters=search_filters if isinstance(search_filters, dict) else {},
            limit=limit,
        )
        structured = await self._repository.search_by_filters(
            query.search_filters,
            intent_type=query.intent_type,
            limit=query.limit,
        )
        if structured:
            return [self._to_item(hit) for hit in structured]

        seen: set[str] = set()
        out: list[SearchItemDto] = []
        queries: list[str] = []
        if query.refined_query.strip():
            queries.append(query.refined_query.strip())
        for keyword in query.keywords:
            key = keyword.strip()
            if key and key not in queries:
                queries.append(key)
        for q in queries[: query.limit]:
            for item in await self.search(q, limit=8):
                if item.id in seen:
                    continue
                seen.add(item.id)
                out.append(item)
                if len(out) >= query.limit:
                    return out
        return out
