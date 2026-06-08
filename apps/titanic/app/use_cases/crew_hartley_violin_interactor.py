from __future__ import annotations

import logging

from titanic.adapter.inbound.api.schemas.crew_hartley_violin_schema import HartleyViolinSchema
from titanic.app.dtos.crew_hartley_violin_dto import HartleyViolinQuery, HartleyViolinResponse
from titanic.app.ports.input.crew_hartley_violin_use_case import HartleyViolinUseCase
from titanic.app.ports.output.crew_hartley_violin_repository import HartleyViolinRepository

logger = logging.getLogger(__name__)


class HartleyViolinInteractor(HartleyViolinUseCase):
    def __init__(self, repository: HartleyViolinRepository) -> None:
        self._repository = repository

    async def introduce_myself(self, schemas: HartleyViolinSchema) -> HartleyViolinResponse:
        query = HartleyViolinQuery(
            id=schemas.id,
            name=schemas.name,
        )
        logger.info("🤖 [HartleyViolinUseCase] 라우터에서 가져온 하틀리 정보 — id=%s", query.id)
        self._repository.introduce_myself(query)
        return HartleyViolinResponse(id=query.id, name=query.name)
