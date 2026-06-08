from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.oracle_database import get_db
from fastapi import Depends

from titanic.adapter.outbound.pg.crew_andrews_architect_pg_repository import AndrewsBlueprintPgRepository
from titanic.app.ports.input.crew_andrews_architect_use_case import AndrewsBlueprintUseCase
from titanic.app.ports.output.crew_andrews_architect_repository import AndrewsBlueprintRepository
from titanic.app.use_cases.crew_andrews_architect_interactor import AndrewsBlueprintInteractor


def get_crew_andrews_architect_use_case(db: AsyncSession = Depends(get_db)) -> AndrewsBlueprintUseCase:
    repository: AndrewsBlueprintRepository = AndrewsBlueprintPgRepository(session=db)
    return AndrewsBlueprintInteractor(repository=repository)
