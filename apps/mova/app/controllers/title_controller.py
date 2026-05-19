import logging

from mova.app.schemas.title_schema import MovaSearchItemSchema, MovaTitleDetailSchema
from mova.app.services.title_service import TitleService

logger = logging.getLogger(__name__)


class TitleController:
    def __init__(self) -> None:
        self.title_service = TitleService()

    async def search(self, query: str, limit: int = 12) -> list[MovaSearchItemSchema]:
        logger.info("[TitleController] search 진입 — q=%r", query)
        return await self.title_service.search(query, limit=limit)

    async def get_detail(self, slug: str) -> MovaTitleDetailSchema | None:
        logger.info("[TitleController] get_detail 진입 — slug=%s", slug)
        return await self.title_service.get_detail(slug)
