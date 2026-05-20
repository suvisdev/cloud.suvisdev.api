import logging
from datetime import date

from mova.app.schemas.rankings_schema import (
    HotRankingDisplaySchema,
    RankingBulkSchema,
)
from mova.app.services.rankings_service import RankingsService

logger = logging.getLogger(__name__)


class RankingsController:
    def __init__(self) -> None:
        self.rankings_service = RankingsService()

    async def save_rankings(self, payload: RankingBulkSchema) -> list[HotRankingDisplaySchema]:
        logger.info("[RankingsController] save_rankings — count=%s", len(payload.items))
        return await self.rankings_service.save_rankings(payload)

    async def list_hot_rankings(
        self,
        *,
        ranked_at: date | None = None,
        limit: int = 20,
    ) -> list[HotRankingDisplaySchema]:
        return await self.rankings_service.list_hot_rankings(
            ranked_at=ranked_at,
            limit=limit,
        )
