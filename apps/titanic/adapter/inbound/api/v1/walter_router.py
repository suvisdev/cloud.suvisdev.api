import logging

from fastapi import APIRouter, Query

from titanic.app.dtos.walter_dto import WalterPassengerPage
from titanic.app.use_cases.walter_query import WalterQuery

walter_router = APIRouter(prefix="/titanic/walter", tags=["titanic-walter"])
logger = logging.getLogger(__name__)


@walter_router.get("/passengers", response_model=WalterPassengerPage)
async def get_passenger_page(
    page: int = Query(default=1, ge=1, description="1부터 시작하는 페이지 번호"),
) -> WalterPassengerPage:
    # 요구사항: 화면에는 50명 단위 목록
    logger.info("🤖 [WalterRouter] get_passenger_page 진입 — page=%s page_size=50", page)
    result = await WalterQuery().get_passenger_page(page, 50)
    logger.info(
        "🤖 [WalterRouter] get_passenger_page 완료 — page=%s items=%s total=%s",
        result.page,
        len(result.items),
        result.total_count,
    )
    return result
