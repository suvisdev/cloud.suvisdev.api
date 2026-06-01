from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.output.smith_captain_repository import SmithCaptainRepository

logger = logging.getLogger(__name__)


class SmithCaptainPgRepository(SmithCaptainRepository):
    """Titanic Smith 선장 조회 — Neon(PostgreSQL) 아웃바운드 어댑터 (포트 구현)."""

    def __init__(self, repository: SmithCaptainRepository | None = None) -> None:
        self._repository = repository

    async def get_captain(self, request: dict[str, Any]) -> int:
        logger.info(
            "🤖 [SmithCaptainPgRepository] get_captain 진입 (Neon) — request=%s",
            request,
        )
        result = 0
        logger.info("🤖 [SmithCaptainPgRepository] get_captain 완료 — result=%s", result)
        return result
