from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.dtos.crew_walter_roaster_dto import WalterQuery
from titanic.app.ports.output.crew_walter_roaster_repository import WalterRepository

logger = logging.getLogger(__name__)


class WalterPgRepository(WalterRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def introduce_myself(self, query: WalterQuery) -> None:
        logger.info("🤖 [WalterRepository] 유스케이스에서 가져온 월터 정보")
        logger.info("🤖 ID: %s", query.id)
        logger.info("🤖 Name: %s", query.name)
        logger.info("🤖 Memo: %s", query.memo)
