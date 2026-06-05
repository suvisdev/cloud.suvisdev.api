from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.oracle_database import get_db
from fastapi import Depends

from mova.adapter.outbound.pg.actors_pg_repository import ActorsPgRepository
from mova.app.ports.input.actors_use_case import ActorsUseCase
from mova.app.ports.output.actors_repository import ActorsRepository
from mova.app.use_cases.actors_interactor import ActorsInteractor


def get_actors_use_case(db: AsyncSession = Depends(get_db)) -> ActorsUseCase:
    repository: ActorsRepository = ActorsPgRepository(session=db)
    return ActorsInteractor(repository=repository)
