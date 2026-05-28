from __future__ import annotations

import logging

from titanic.app.dtos.walter_dto import WalterPassengerPage
from titanic.app.walter_reader import WalterReader

logger = logging.getLogger(__name__)


class WalterQuery:
    """입력 포트 전용 조회 유스케이스(페이지 계산/조합)."""

    def __init__(self, reader: WalterReader | None = None) -> None:
        self._reader = reader or WalterReader()

    async def get_passenger_page(self, *, page: int, page_size: int) -> WalterPassengerPage:
        logger.info(
            "[WalterQuery] get_passenger_page 진입 — page=%s page_size=%s",
            page,
            page_size,
        )
        safe_page = max(1, page)
        safe_size = max(1, page_size)
        offset = (safe_page - 1) * safe_size

        total_count = await self._reader.get_total_count()
        items = await self._reader.get_passengers(offset=offset, limit=safe_size)
        total_pages = (total_count + safe_size - 1) // safe_size if total_count else 0

        result = WalterPassengerPage(
            page=safe_page,
            page_size=safe_size,
            total_count=total_count,
            total_pages=total_pages,
            items=items,
        )
        logger.info(
            "[WalterQuery] get_passenger_page 완료 — page=%s items=%s total=%s",
            result.page,
            len(result.items),
            result.total_count,
        )
        return result


__all__ = ["WalterQuery"]
