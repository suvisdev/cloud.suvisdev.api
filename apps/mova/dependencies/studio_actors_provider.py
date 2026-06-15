from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.grid_oracle_database_manager import get_db
from fastapi import Depends

from mova.adapter.outbound.pg.studio_actors_pg_repository import StudioActorsPgRepository
from mova.app.ports.input.studio_actors_use_case import StudioActorsUseCase
from mova.app.ports.output.studio_actors_repository import StudioActorsRepository
from mova.app.use_cases.studio_actors_interactor import StudioActorsInteractor


def get_studio_actors_repository(
    db: AsyncSession = Depends(get_db),
) -> StudioActorsRepository:
    return StudioActorsPgRepository(session=db)


def get_studio_actors_use_case(
    repository: StudioActorsRepository = Depends(get_studio_actors_repository),
) -> StudioActorsUseCase:
    return StudioActorsInteractor(repository=repository)
