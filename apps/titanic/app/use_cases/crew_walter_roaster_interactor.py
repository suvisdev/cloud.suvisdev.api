from __future__ import annotations

import logging

from titanic.adapter.inbound.api.schemas.crew_walter_roaster_schema import WalterSchema
from titanic.app.dtos.crew_walter_roaster_dto import WalterQuery, WalterResponse
from titanic.app.ports.input.crew_walter_roaster_use_case import WalterUseCase
from titanic.app.ports.output.crew_walter_roaster_repository import WalterRepository

logger = logging.getLogger(__name__)


class WalterInteractor(WalterUseCase):
    def __init__(self, repository: WalterRepository) -> None:
        self._repository = repository

    async def introduce_myself(self, schemas: WalterSchema) -> WalterResponse:
        query = WalterQuery(
            id=schemas.id,
            name=schemas.name,
            memo=schemas.memo,
        )
        logger.info("🤖 [WalterUseCase] 라우터에서 가져온 월터 정보 — id=%s", query.id)
        self._repository.introduce_myself(query)
        return WalterResponse(id=query.id, name=query.name, memo=query.memo)