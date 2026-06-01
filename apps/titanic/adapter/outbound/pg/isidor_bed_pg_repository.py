from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.output.isidor_bed_repository import IsidorBedRepository

logger = logging.getLogger(__name__)


class IsidorBedPgRepository(IsidorBedRepository):
    """Titanic Isidor 침대 조회 — Neon(PostgreSQL) 아웃바운드 어댑터 (포트 구현)."""

    def __init__(self, repository: IsidorBedRepository | None = None) -> None:
        self._repository = repository

    async def get_bed(self, request: dict[str, Any]) -> int:
        logger.info(
            "🤖 [IsidorBedPgRepository] get_bed 진입 (Neon) — request=%s",
            request,
        )
        result = 0
        logger.info("🤖 [IsidorBedPgRepository] get_bed 완료 — result=%s", result)
        return result
