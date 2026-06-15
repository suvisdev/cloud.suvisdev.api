from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.grid_oracle_database_manager import get_db
from fastapi import Depends

from mova.adapter.outbound.pg.market_rankings_pg_repository import MarketRankingsPgRepository
from mova.app.ports.input.market_rankings_use_case import MarketRankingsUseCase
from mova.app.ports.output.market_rankings_repository import MarketRankingsRepository
from mova.app.use_cases.market_rankings_interactor import MarketRankingsInteractor


def get_market_rankings_repository(
    db: AsyncSession = Depends(get_db),
) -> MarketRankingsRepository:
    return MarketRankingsPgRepository(session=db)


def get_market_rankings_use_case(
    repository: MarketRankingsRepository = Depends(get_market_rankings_repository),
) -> MarketRankingsUseCase:
    return MarketRankingsInteractor(repository=repository)
