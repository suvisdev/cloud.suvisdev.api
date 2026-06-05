from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.oracle_database import get_db
from fastapi import Depends

from mova.adapter.outbound.pg.rankings_pg_repository import RankingsPgRepository
from mova.app.ports.input.rankings_use_case import RankingsUseCase
from mova.app.ports.output.rankings_repository import RankingsRepository
from mova.app.use_cases.rankings_interactor import RankingsInteractor


def get_rankings_use_case(db: AsyncSession = Depends(get_db)) -> RankingsUseCase:
    repository: RankingsRepository = RankingsPgRepository(session=db)
    return RankingsInteractor(repository=repository)
