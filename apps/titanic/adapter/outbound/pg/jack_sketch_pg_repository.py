from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.output.jack_sketch_repository import JackSketchRepository

logger = logging.getLogger(__name__)


class JackSketchPgRepository(JackSketchRepository):
    """Titanic Jack 스케치 조회 — Neon(PostgreSQL) 아웃바운드 어댑터 (포트 구현)."""

    def __init__(self, repository: JackSketchRepository | None = None) -> None:
        self._repository = repository

    async def get_sketch(self, request: dict[str, Any]) -> int:
        logger.info(
            "🤖 [JackSketchPgRepository] get_sketch 진입 (Neon) — request=%s",
            request,
        )
        result = 0
        logger.info("🤖 [JackSketchPgRepository] get_sketch 완료 — result=%s", result)
        return result
