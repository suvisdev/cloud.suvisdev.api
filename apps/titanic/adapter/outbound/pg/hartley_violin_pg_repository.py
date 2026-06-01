from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.output.hartley_violin_repository import HartleyViolinRepository

logger = logging.getLogger(__name__)


class HartleyViolinPgRepository(HartleyViolinRepository):
    """Titanic Hartley 바이올린 조회 — Neon(PostgreSQL) 아웃바운드 어댑터 (포트 구현)."""

    def __init__(self, repository: HartleyViolinRepository | None = None) -> None:
        self._repository = repository

    async def get_violin(self, request: dict[str, Any]) -> int:
        logger.info(
            "🤖 [HartleyViolinPgRepository] get_violin 진입 (Neon) — request=%s",
            request,
        )
        result = 0
        logger.info("🤖 [HartleyViolinPgRepository] get_violin 완료 — result=%s", result)
        return result
