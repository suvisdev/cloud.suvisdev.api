from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.oracle_database import get_db
from fastapi import Depends

from titanic.app.ports.input.james_use_case import JamesUseCase
from titanic.app.use_cases.james_interactor import JamesInteractor
from titanic.adapter.outbound.pg.james_pg_repository import JamesPgRepository
from titanic.app.ports.output.james_repository import JamesRepository


def get_james_use_case(db: AsyncSession = Depends(get_db)) -> JamesUseCase:
    repository: JamesRepository = JamesPgRepository(session=db)
    return JamesInteractor(repository=repository)
