from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.ports.output.passenger_molly_scaler_repository import MollyScalerRepository

logger = logging.getLogger(__name__)


class MollyScalerPgRepository(MollyScalerRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def get_scaler(self, request: dict[str, Any]) -> int:
        logger.info("[%s] %s request=%s", "MollyScalerPgRepository", "get_scaler", request)
        return 0
