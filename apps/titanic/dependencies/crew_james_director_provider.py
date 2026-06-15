from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.grid_oracle_database_manager import get_db
from fastapi import Depends

from titanic.adapter.outbound.pg.crew_james_director_pg_repository import JamesPgRepository
from titanic.app.ports.input.crew_james_director_use_case import JamesUseCase
from titanic.app.ports.output.crew_james_director_repository import JamesRepository
from titanic.app.use_cases.crew_james_director_interactor import JamesInteractor


def get_james_director_repository(
        db: AsyncSession = Depends(get_db)
) -> JamesRepository:
    return JamesPgRepository(session=db)

def get_james_director_use_case(
        repository: JamesRepository = Depends(get_james_director_repository)
) -> JamesUseCase:
    return JamesInteractor(repository=repository)
