from __future__ import annotations

from mova.adapter.inbound.api.schemas.market_rankings_schema import MarketRankingsSchema
from mova.app.dtos.market_rankings_dto import MarketRankingsQuery, MarketRankingsResponse
from mova.app.ports.input.market_rankings_use_case import MarketRankingsUseCase
from mova.app.ports.output.market_rankings_repository import MarketRankingsRepository


class MarketRankingsInteractor(MarketRankingsUseCase):
    def __init__(self, repository: MarketRankingsRepository) -> None:
        self._repository = repository

    async def introduce_myself(self, schemas: MarketRankingsSchema) -> MarketRankingsResponse:
        return await self._repository.introduce_myself(MarketRankingsQuery(
            id=schemas.id,
            name=schemas.name,
        ))
