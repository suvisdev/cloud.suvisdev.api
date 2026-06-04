import logging

from titanic.app.ports.output.walter_repository import WalterRepository
from titanic.app.dtos.walter_dto import WalterQuery

logger = logging.getLogger(__name__)


class WalterPgRepository(WalterRepository):
    def __init__(self):
        pass


    def introduce_myself(self, query: WalterQuery):
        

         # 🎁로그 코드 시작
        logger.info("🎁로그 시작#########################################")
        logger.info("🤖 [WalterRepository] 유스케이스에서 가져온 월터 정보")
        logger.info(f"🤖 ID: {query.id}")
        logger.info(f"🤖 Name: {query.name}")
        logger.info(f"🤖 Memo: {query.memo}")
        logger.info("🎁로그 끝#######################################")
        # 🎁로그 코드 끝

        pass