from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.output.rose_diamond_repository import RoseDiamondRepository

logger = logging.getLogger(__name__)


class RoseDiamondPgRepository(RoseDiamondRepository):
    """Titanic Rose 다이아몬드 조회 — Neon(PostgreSQL) 아웃바운드 어댑터 (포트 구현)."""

    def __init__(self, repository: RoseDiamondRepository | None = None) -> None:
        self._repository = repository

    async def get_diamond(self, request: dict[str, Any]) -> int:
        logger.info(
            "🤖 [RoseDiamondPgRepository] get_diamond 진입 (Neon) — request=%s",
            request,
        )
        result = 0
        logger.info("🤖 [RoseDiamondPgRepository] get_diamond 완료 — result=%s", result)
        return result
