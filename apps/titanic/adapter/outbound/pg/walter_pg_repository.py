import logging

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.dtos.walter_dto import WalterQuery
from titanic.app.ports.output.walter_repository import WalterRepository

logger = logging.getLogger(__name__)


class WalterPgRepository(WalterRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def introduce_myself(self, query: WalterQuery):
        # 🎁로그 코드 시작
        logger.info("🎁로그 시작#########################################")
        logger.info("🤖 [WalterRepository] 유스케이스에서 가져온 월터 정보")
        logger.info(f"🤖 ID: {query.id}")
        logger.info(f"🤖 Name: {query.name}")
        logger.info(f"🤖 Memo: {query.memo}")
        logger.info("🎁로그 끝#######################################")
        # 🎁로그 코드 끝
