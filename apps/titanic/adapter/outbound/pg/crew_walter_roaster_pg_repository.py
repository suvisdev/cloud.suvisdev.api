from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.dtos.crew_walter_roaster_dto import WalterQuery, WalterResponse
from titanic.app.ports.output.crew_walter_roaster_repository import WalterRepository

logger = logging.getLogger(__name__)


class WalterPgRepository(WalterRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def introduce_myself(self, query: WalterQuery) -> WalterResponse:
        logger.info(f"[WalterPgRepository] introduce_myself 진입 | request_data={query}")
        response = WalterResponse(id=query.id * 10000, name=query.name + "가 레포지토리에 다녀옴")
        return response
