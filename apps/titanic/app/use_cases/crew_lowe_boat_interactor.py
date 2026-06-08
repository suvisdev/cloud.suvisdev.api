from __future__ import annotations

import logging

from titanic.adapter.inbound.api.schemas.crew_lowe_boat_schema import LoweBoatSchema
from titanic.app.dtos.crew_lowe_boat_dto import LoweBoatQuery, LoweBoatResponse
from titanic.app.ports.input.crew_lowe_boat_use_case import LoweBoatUseCase
from titanic.app.ports.output.crew_lowe_boat_repository import LoweBoatRepository

logger = logging.getLogger(__name__)


class LoweBoatInteractor(LoweBoatUseCase):
    def __init__(self, repository: LoweBoatRepository) -> None:
        self._repository = repository

    async def introduce_myself(self, schemas: LoweBoatSchema) -> LoweBoatResponse:
        query = LoweBoatQuery(
            id=schemas.id,
            name=schemas.name,
        )
        logger.info("🤖 [LoweBoatUseCase] 라우터에서 가져온 로우 정보 — id=%s", query.id)
        self._repository.introduce_myself(query)
        return LoweBoatResponse(id=query.id, name=query.name)
