from __future__ import annotations

import logging
from typing import Protocol

from titanic.app.dtos.walter_dto import WalterPassengerPage
from titanic.app.use_cases.walter_query import WalterQuery

logger = logging.getLogger(__name__)


class WalterUseCasePort(Protocol):
    async def get_passenger_page(self, *, page: int, page_size: int) -> WalterPassengerPage: ...


class WalterUseCase(WalterUseCasePort):
    """승객 목록 조회 유스케이스."""

    def __init__(self, query: WalterQuery | None = None) -> None:
        self._query = query or WalterQuery()

    async def get_passenger_page(self, *, page: int, page_size: int) -> WalterPassengerPage:
        logger.info(
            "[WalterUseCase] get_passenger_page 진입 — page=%s page_size=%s",
            page,
            page_size,
        )
        result = await self._query.get_passenger_page(
            page=page,
            page_size=page_size,
        )
        logger.info(
            "[WalterUseCase] get_passenger_page 완료 — page=%s items=%s total=%s",
            result.page,
            len(result.items),
            result.total_count,
        )
        return result
