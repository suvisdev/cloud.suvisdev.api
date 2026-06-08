from __future__ import annotations

import logging

from titanic.adapter.inbound.api.schemas.crew_andrews_architect_schema import AndrewsArchitectSchema
from titanic.app.dtos.crew_andrews_architect_dto import AndrewsArchitectQuery, AndrewsArchitectResponse
from titanic.app.ports.input.crew_andrews_architect_use_case import AndrewsArchitectUseCase
from titanic.app.ports.output.crew_andrews_architect_repository import AndrewsArchitectRepository

logger = logging.getLogger(__name__)


class AndrewsArchitectInteractor(AndrewsArchitectUseCase):
    def __init__(self, repository: AndrewsArchitectRepository) -> None:
        self._repository = repository

    async def introduce_myself(
        self,
        schemas: AndrewsArchitectSchema,
    ) -> AndrewsArchitectResponse:
        query = AndrewsArchitectQuery(
            id=schemas.id,
            name=schemas.name,
        )
        logger.info(
            "🤖 [AndrewsArchitectUseCase] 라우터에서 가져온 앤드류스 정보 — id=%s",
            query.id,
        )
        self._repository.introduce_myself(query)
        return AndrewsArchitectResponse(id=query.id, name=query.name)
