from __future__ import annotations

import logging
from typing import Any

from titanic.app.ports.input.passenger_molly_scaler_use_case import MollyScalerUseCase
from titanic.app.ports.output.passenger_molly_scaler_repository import MollyScalerRepository

logger = logging.getLogger(__name__)


class MollyScalerInteractor(MollyScalerUseCase):
    def __init__(self, repository: MollyScalerRepository) -> None:
        self._repository = repository

    async def get_scaler(self, request: dict[str, Any]) -> int:
        logger.info("[%s] %s", "MollyScalerInteractor", "get_scaler")
        return await self._repository.get_scaler(request)
