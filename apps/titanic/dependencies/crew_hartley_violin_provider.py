from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.oracle_database import get_db
from fastapi import Depends

from titanic.adapter.outbound.pg.crew_hartley_violin_pg_repository import HartleyViolinPgRepository
from titanic.app.ports.input.crew_hartley_violin_use_case import HartleyViolinUseCase
from titanic.app.ports.output.crew_hartley_violin_repository import HartleyViolinRepository
from titanic.app.use_cases.crew_hartley_violin_interactor import HartleyViolinInteractor


def get_hartley_violin_use_case(db: AsyncSession = Depends(get_db)) -> HartleyViolinUseCase:
    repository: HartleyViolinRepository = HartleyViolinPgRepository(session=db)
    return HartleyViolinInteractor(repository=repository)
