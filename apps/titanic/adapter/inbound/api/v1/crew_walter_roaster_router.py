from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from titanic.adapter.inbound.api.schemas.crew_walter_roaster_schema import WalterSchema
from titanic.app.dtos.crew_walter_roaster_dto import WalterResponse
from titanic.app.ports.input.crew_walter_roaster_use_case import WalterUseCase
from titanic.dependencies.crew_walter_roaster import get_crew_walter_roaster_use_case

crew_walter_roaster_router = APIRouter(prefix="/walter", tags=["walter"])
logger = logging.getLogger(__name__)


@crew_walter_roaster_router.get("/myself")
async def introduce_myself(
    walter: WalterUseCase = Depends(get_crew_walter_roaster_use_case),
) -> WalterResponse:
    return await walter.introduce_myself(
        WalterSchema(
            id=2,
            name="Walter",
            memo="타이타닉의 일등 항해사, 승객 명단 관리 담당",
        )
    )
