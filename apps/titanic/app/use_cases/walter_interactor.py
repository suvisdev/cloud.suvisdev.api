import logging

from titanic.adapter.inbound.api.schemas.walter_schema import WalterSchema
from titanic.app.dtos.walter_dto import WalterQuery
from titanic.app.ports.input.walter_use_case import WalterUseCase
from titanic.app.ports.output.walter_repository import WalterRepository
from titanic.adapter.outbound.pg.walter_pg_repository import WalterPgRepository

logger = logging.getLogger(__name__)

class WalterInteractor(WalterUseCase):

    def __init__(self):
        pass

    def introduce_myself(self, schemas: WalterSchema):


        # 스키마에 저장된 정보를 쿼리에 옮겨 담는 코드 구현
        query = WalterQuery(
            id=schemas.id,
            name=schemas.name,
            memo=schemas.memo,
        )

        # 🎁로그 코드 시작
        logger.info("🎁로그 시작#########################################")
        logger.info("🤖 [WalterUseCase] 라우터에서 가져온 월터 정보")
        logger.info(f"🤖 ID: {query.id}")
        logger.info(f"🤖 Name: {query.name}")
        logger.info(f"🤖 Memo: {query.memo}")
        logger.info("🎁로그 끝#######################################")
        # 🎁로그 코드 끝

        walter : WalterRepository = WalterPgRepository()
        walter.introduce_myself(query)

        pass