from __future__ import annotations

import logging

from titanic.adapter.inbound.api.schemas.passenger_molly_scaler_schema import MollyScalerSchema
from titanic.app.dtos.passenger_molly_scaler_dto import MollyScalerQuery, MollyScalerResponse
from titanic.app.ports.input.passenger_molly_scaler_use_case import MollyScalerUseCase
from titanic.app.ports.output.passenger_molly_scaler_repository import MollyScalerRepository

logger = logging.getLogger(__name__)


class MollyScalerInteractor(MollyScalerUseCase):
    def __init__(self, repository: MollyScalerRepository) -> None:
        self._repository = repository

    async def introduce_myself(self, schemas: MollyScalerSchema) -> MollyScalerResponse:
        query = MollyScalerQuery(
            id=schemas.id,
            name=schemas.name,
        )
        logger.info("🤖 [MollyScalerUseCase] 라우터에서 가져온 몰리 정보 — id=%s", query.id)
        self._repository.introduce_myself(query)
        return MollyScalerResponse(id=query.id, name=query.name)
