from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.oracle_database import get_db
from fastapi import Depends

from titanic.adapter.outbound.pg.crew_james_director_pg_repository import JamesPgRepository
from titanic.app.ports.input.crew_james_director_use_case import JamesUseCase
from titanic.app.ports.output.crew_james_director_repository import JamesRepository
from titanic.app.use_cases.crew_james_director_interactor import JamesInteractor


def get_crew_james_director_use_case(db: AsyncSession = Depends(get_db)) -> JamesUseCase:
    repository: JamesRepository = JamesPgRepository(session=db)
    return JamesInteractor(repository=repository)
