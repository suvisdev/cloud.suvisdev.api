from fastapi import APIRouter
import logging
from fastapi import Depends

from titanic.adapter.inbound.api.schemas.walter_schema import WalterSchema
from titanic.app.ports.input.walter_use_case import WalterUseCase
from titanic.dependencies.walter import get_walter_use_case
from titanic.app.dtos.walter_dto import WalterResponse

walter_router = APIRouter(prefix="/walter", tags=["walter"])
logger = logging.getLogger(__name__)



@walter_router.get("/myself")
async def introduce_myself(
    walter: WalterUseCase = Depends(get_walter_use_case)
) -> WalterResponse:
   
    return await walter.introduce_myself(
        WalterSchema(
            id=2,
            name="Walter",
            memo="타이타닉의 일등 항해사, 승객 명단 관리 담당")
        )
