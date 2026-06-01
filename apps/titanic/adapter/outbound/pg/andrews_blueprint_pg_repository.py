from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.output.andrews_blueprint_repository import AndrewsBlueprintRepository

logger = logging.getLogger(__name__)


class AndrewsBlueprintPgRepository(AndrewsBlueprintRepository):
    """Titanic Andrews 설계도 조회 — Neon(PostgreSQL) 아웃바운드 어댑터 (포트 구현)."""

    def __init__(self, repository: AndrewsBlueprintRepository | None = None) -> None:
        self._repository = repository

    async def get_blueprint(self, request: dict[str, Any]) -> int:
        logger.info(
            "🤖 [AndrewsBlueprintPgRepository] get_blueprint 진입 (Neon) — request=%s",
            request,
        )
        result = 0
        logger.info("🤖 [AndrewsBlueprintPgRepository] get_blueprint 완료 — result=%s", result)
        return result
