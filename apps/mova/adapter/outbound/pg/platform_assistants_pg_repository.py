from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from mova.app.dtos.platform_assistants_dto import PlatformAssistantsQuery, PlatformAssistantsResponse
from mova.app.ports.output.platform_assistants_repository import PlatformAssistantsRepository

logger = logging.getLogger(__name__)


class PlatformAssistantsPgRepository(PlatformAssistantsRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def introduce_myself(self, query: PlatformAssistantsQuery) -> PlatformAssistantsResponse:
        logger.info("[PlatformAssistantsPgRepository] introduce_myself | query=%s", query)
        return PlatformAssistantsResponse(id=query.id * 10000, name=query.name + "가 레포지토리에 다녀옴")
