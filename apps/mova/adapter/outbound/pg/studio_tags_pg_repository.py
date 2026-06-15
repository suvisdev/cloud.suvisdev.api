from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from mova.app.dtos.studio_tags_dto import StudioTagsQuery, StudioTagsResponse
from mova.app.ports.output.studio_tags_repository import StudioTagsRepository

logger = logging.getLogger(__name__)


class StudioTagsPgRepository(StudioTagsRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def introduce_myself(self, query: StudioTagsQuery) -> StudioTagsResponse:
        logger.info("[StudioTagsPgRepository] introduce_myself | query=%s", query)
        return StudioTagsResponse(id=query.id * 10000, name=query.name + "가 레포지토리에 다녀옴")
