from fastapi import APIRouter
import logging

from titanic.adapter.inbound.api.schemas.walter_schema import WalterSchema
from titanic.app.ports.input.walter_use_case import WalterUseCase
from titanic.app.use_cases.walter_interactor import WalterInteractor

walter_router = APIRouter(prefix="/walter", tags=["walter"])
logger = logging.getLogger(__name__)



@walter_router.get("/myself", status_code=204)
async def introduce_myself() -> None:
    schema = WalterSchema()

    # 🎁로그 코드 시작
    logger.info("🎁로그 시작#########################################")
    logger.info("🤖 [WalterRouter] Walter의 자기소개글을 가져오는 API 호출")
    logger.info(f"🤖 ID: {schema.id}")
    logger.info(f"🤖 Name: {schema.name}")
    logger.info(f"🤖 Memo: {schema.memo}")
    logger.info("🎁로그 끝#######################################")
    # 🎁로그 코드 끝

    walter: WalterUseCase = WalterInteractor()
    walter.introduce_myself(schema)

    pass


