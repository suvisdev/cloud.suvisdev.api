from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.dtos.crew_hartley_violin_dto import HartleyViolinQuery, HartleyViolinResponse
from titanic.app.ports.output.crew_hartley_violin_repository import HartleyViolinRepository

logger = logging.getLogger(__name__)


class HartleyViolinPgRepository(HartleyViolinRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def introduce_myself(self, query: HartleyViolinQuery) -> HartleyViolinResponse:
        logger.info(f"[HartleyViolinPgRepository] introduce_myself 진입 | request_data={query}")
        response = HartleyViolinResponse(id=query.id * 10000, name=query.name + "가 레포지토리에 다녀옴")
        return response
