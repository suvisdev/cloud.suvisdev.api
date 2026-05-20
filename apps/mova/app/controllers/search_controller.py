import logging

from mova.app.schemas.search_schema import MovaSearchItemSchema
from mova.app.services.search_service import SearchService

logger = logging.getLogger(__name__)


class SearchController:
    def __init__(self) -> None:
        self.search_service = SearchService()

    async def search(self, query: str, *, limit: int = 12) -> list[MovaSearchItemSchema]:
        logger.info("[SearchController] search — q=%r", query.strip())
        return await self.search_service.search(query, limit=limit)
