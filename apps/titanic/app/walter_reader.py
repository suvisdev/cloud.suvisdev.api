from __future__ import annotations

import logging

from titanic.app.dtos.walter_dto import WalterPassengerItem
from titanic.app.ports.output.walter_reader import WalterReader as WalterOutputReader

logger = logging.getLogger(__name__)


class WalterReader:
    """앱 레이어 파사드 (Query -> OutputPort Reader 연결점)."""

    def __init__(self, reader: WalterOutputReader | None = None) -> None:
        self._reader = reader or WalterOutputReader()

    async def get_passengers(self, *, offset: int, limit: int) -> list[WalterPassengerItem]:
        logger.info(
            "[WalterAppReader] get_passengers 진입 — offset=%s limit=%s",
            offset,
            limit,
        )
        items = await self._reader.get_passengers(offset=offset, limit=limit)
        logger.info("[WalterAppReader] get_passengers 완료 — items=%s", len(items))
        return items

    async def get_total_count(self) -> int:
        logger.info("[WalterAppReader] get_total_count 진입")
        total = await self._reader.get_total_count()
        logger.info("[WalterAppReader] get_total_count 완료 — total=%s", total)
        return total

