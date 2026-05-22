import logging
from typing import Any

from mova.app.data.movie_catalog import resolve_canonical_slug
from mova.app.repositories.search_repository import SearchHit, SearchRepository
from mova.app.schemas.search_schema import MovaSearchItemSchema

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self) -> None:
        self.repository = SearchRepository()

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
        logger.info("[SearchService] search — q=%r limit=%s", q, limit)
        hits = await self.repository.search(q, limit=limit)
        return [self._to_item(h) for h in hits]

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
        structured = await self.repository.search_by_filters(
            filters,
            intent_type=intent_type or "mood",
            limit=limit,
        )
        if structured:
            logger.info(
                "[SearchService] search_by_intent — type=%s structured_hits=%s",
                intent_type,
                len(structured),
            )
            return [self._to_item(h) for h in structured]

        seen: set[str] = set()
        out: list[MovaSearchItemSchema] = []
        queries: list[str] = []
        if refined_query.strip():
            queries.append(refined_query.strip())
        for kw in keywords:
            k = kw.strip()
            if k and k not in queries:
                queries.append(k)
        for q in queries[:limit]:
            for item in await self.search(q, limit=8):
                if item.id in seen:
                    continue
                seen.add(item.id)
                out.append(item)
                if len(out) >= limit:
                    return out
        return out
