from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from mova.app.dtos.studio_search_dto import StudioSearchQuery, StudioSearchResponse
from mova.app.ports.output.studio_search_repository import StudioSearchRepository

logger = logging.getLogger(__name__)


class StudioSearchPgRepository(StudioSearchRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def introduce_myself(self, query: StudioSearchQuery) -> StudioSearchResponse:
        logger.info("[StudioSearchPgRepository] introduce_myself | query=%s", query)
        return StudioSearchResponse(id=query.id * 10000, name=query.name + "가 레포지토리에 다녀옴")
