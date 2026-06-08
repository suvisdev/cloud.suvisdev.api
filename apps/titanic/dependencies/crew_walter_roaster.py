from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.oracle_database import get_db
from fastapi import Depends

from titanic.adapter.outbound.pg.crew_walter_roaster_pg_repository import WalterPgRepository
from titanic.app.ports.input.crew_walter_roaster_use_case import WalterUseCase
from titanic.app.ports.output.crew_walter_roaster_repository import WalterRepository
from titanic.app.use_cases.crew_walter_roaster_interactor import WalterInteractor


def get_crew_walter_roaster_use_case(db: AsyncSession = Depends(get_db)) -> WalterUseCase:
    repository: WalterRepository = WalterPgRepository(session=db)
    return WalterInteractor(repository=repository)
