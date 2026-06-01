from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.output.ruth_corset_repository import RuthCorsetRepository

logger = logging.getLogger(__name__)


class RuthCorsetPgRepository(RuthCorsetRepository):
    """Titanic Ruth 코르셋 조회 — Neon(PostgreSQL) 아웃바운드 어댑터 (포트 구현)."""

    def __init__(self, repository: RuthCorsetRepository | None = None) -> None:
        self._repository = repository

    async def get_corset(self, request: dict[str, Any]) -> int:
        logger.info(
            "🤖 [RuthCorsetPgRepository] get_corset 진입 (Neon) — request=%s",
            request,
        )
        result = 0
        logger.info("🤖 [RuthCorsetPgRepository] get_corset 완료 — result=%s", result)
        return result
