from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.output.cal_pistol_repository import CalPistolRepository

logger = logging.getLogger(__name__)


class CalPistolPgRepository(CalPistolRepository):
    """Titanic Cal 권총 조회 — Neon(PostgreSQL) 아웃바운드 어댑터 (포트 구현)."""

    def __init__(self, repository: CalPistolRepository | None = None) -> None:
        self._repository = repository

    async def get_pistol(self, request: dict[str, Any]) -> None:
        logger.info(
            "🤖 [CalPistolPgRepository] get_pistol 진입 (Neon) — request=%s",
            request,
        )
        logger.info("🤖 [CalPistolPgRepository] get_pistol 완료")
