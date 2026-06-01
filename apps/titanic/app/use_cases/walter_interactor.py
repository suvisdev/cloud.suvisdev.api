from __future__ import annotations

import logging

from titanic.adapter.outbound.pg.walter_pg_reader import WalterPgReader
from titanic.app.dtos.walter_dto import WalterPassengerPage
from titanic.app.ports.input.walter_use_case import WalterUseCase
from titanic.app.ports.output.walter_reader import WalterReader

logger = logging.getLogger(__name__)


class WalterInteractor(WalterUseCase):
    """walter_router → 입력 포트 → 출력 포트(reader) → DB."""

    def __init__(self, reader: WalterReader | None = None) -> None:
        self._reader = reader or WalterPgReader()

    async def get_passenger_page(self, page: int, page_size: int) -> WalterPassengerPage:
        logger.info(
            "🤖 [WalterInteractor] get_passenger_page 진입 — page=%s page_size=%s",
            page,
            page_size,
        )
        safe_page = max(1, page)
        safe_size = max(1, page_size)
        offset = (safe_page - 1) * safe_size

        items, total_count = await self._reader.read_passengers_page(offset, safe_size)
        total_pages = (total_count + safe_size - 1) // safe_size if total_count else 0

        result = WalterPassengerPage(
            page=safe_page,
            page_size=safe_size,
            total_count=total_count,
            total_pages=total_pages,
            items=items,
        )
        logger.info(
            "🤖 [WalterInteractor] get_passenger_page 완료 — page=%s items=%s total=%s",
            result.page,
            len(result.items),
            result.total_count,
        )
        return result
