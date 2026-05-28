from __future__ import annotations

import logging
from typing import Protocol

from titanic.adapter.outbound.pg.walter_pg_reader import WalterPgReader
from titanic.app.dtos.walter_dto import WalterPassengerItem

logger = logging.getLogger(__name__)


class WalterReaderPort(Protocol):
    async def get_passengers(self, *, offset: int, limit: int) -> list[WalterPassengerItem]: ...
    async def get_total_count(self) -> int: ...


class WalterReader(WalterReaderPort):
    """애플리케이션 출력 포트 구현체 (Reader -> PgReader 위임)."""

    def __init__(self, pg_reader: WalterPgReader | None = None) -> None:
        self._pg_reader = pg_reader or WalterPgReader()

    async def get_passengers(self, *, offset: int, limit: int) -> list[WalterPassengerItem]:
        logger.info(
            "[WalterReader] get_passengers 진입 — offset=%s limit=%s",
            offset,
            limit,
        )
        items = await self._pg_reader.get_passengers(offset=offset, limit=limit)
        logger.info("[WalterReader] get_passengers 완료 — items=%s", len(items))
        return items

    async def get_total_count(self) -> int:
        logger.info("[WalterReader] get_total_count 진입")
        total = await self._pg_reader.get_total_count()
        logger.info("[WalterReader] get_total_count 완료 — total=%s", total)
        return total
