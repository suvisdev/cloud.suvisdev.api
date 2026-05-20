import logging

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
