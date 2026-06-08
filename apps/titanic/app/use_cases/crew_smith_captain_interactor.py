from __future__ import annotations

import logging

from titanic.adapter.inbound.api.schemas.crew_smith_captain_schema import SmithCaptainSchema
from titanic.app.dtos.crew_smith_captain_dto import SmithCaptainQuery, SmithCaptainResponse
from titanic.app.ports.input.crew_smith_captain_use_case import SmithCaptainUseCase
from titanic.app.ports.output.crew_smith_captain_repository import SmithCaptainRepository

logger = logging.getLogger(__name__)


class SmithCaptainInteractor(SmithCaptainUseCase):
    def __init__(self, repository: SmithCaptainRepository) -> None:
        self._repository = repository

    async def introduce_myself(self, schemas: SmithCaptainSchema) -> SmithCaptainResponse:
        query = SmithCaptainQuery(
            id=schemas.id,
            name=schemas.name,
        )
        logger.info("🤖 [SmithCaptainUseCase] 라우터에서 가져온 스미스 정보 — id=%s", query.id)
        self._repository.introduce_myself(query)
        return SmithCaptainResponse(id=query.id, name=query.name)
