from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.dtos.passenger_molly_scaler_dto import MollyScalerQuery, MollyScalerResponse
from titanic.app.ports.output.passenger_molly_scaler_repository import (
    MollyScalerRepository,
)

logger = logging.getLogger(__name__)


class MollyScalerPgRepository(MollyScalerRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def introduce_myself(self, query: MollyScalerQuery) -> MollyScalerResponse:
        logger.info(f"[MollyScalerPgRepository] introduce_myself 진입 | request_data={query}")
        response = MollyScalerResponse(id=query.id * 10000, name=query.name + "가 레포지토리에 다녀옴")
        return response
