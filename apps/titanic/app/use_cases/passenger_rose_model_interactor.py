from __future__ import annotations

import logging

from titanic.adapter.inbound.api.schemas.passenger_rose_model_schema import RoseModelSchema
from titanic.app.dtos.passenger_rose_model_dto import RoseModelQuery, RoseModelResponse
from titanic.app.ports.input.passenger_rose_model_use_case import RoseModelUseCase
from titanic.app.ports.output.passenger_rose_model_repository import RoseModelRepository

logger = logging.getLogger(__name__)


class RoseModelInteractor(RoseModelUseCase):
    def __init__(self, repository: RoseModelRepository) -> None:
        self._repository = repository

    async def introduce_myself(self, schemas: RoseModelSchema) -> RoseModelResponse:
        query = RoseModelQuery(
            id=schemas.id,
            name=schemas.name,
        )
        logger.info("🤖 [RoseModelUseCase] 라우터에서 가져온 로즈 정보 — id=%s", query.id)
        self._repository.introduce_myself(query)
        return RoseModelResponse(id=query.id, name=query.name)
