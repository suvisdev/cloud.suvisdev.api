"""랭킹 Interactor — RankingsUseCase 구현체."""

from __future__ import annotations

from mova.app.dtos.market_rankings_dto import RankingListDto
from mova.app.ports.input.market_rankings_use_case import RankingsUseCase
from mova.app.ports.output.market_rankings_repository import RankingsRepositoryPort


class RankingsInteractor(RankingsUseCase):
    def __init__(self, repository: RankingsRepositoryPort) -> None:
        self._repository = repository

    async def get_hot(self, source: str, limit: int) -> RankingListDto:
        return await self._repository.get_hot(source, limit)
