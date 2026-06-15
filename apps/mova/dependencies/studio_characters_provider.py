from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.grid_oracle_database_manager import get_db
from fastapi import Depends

from mova.adapter.outbound.pg.studio_characters_pg_repository import StudioCharactersPgRepository
from mova.app.ports.input.studio_characters_use_case import StudioCharactersUseCase
from mova.app.ports.output.studio_characters_repository import StudioCharactersRepository
from mova.app.use_cases.studio_characters_interactor import StudioCharactersInteractor


def get_studio_characters_repository(
    db: AsyncSession = Depends(get_db),
) -> StudioCharactersRepository:
    return StudioCharactersPgRepository(session=db)


def get_studio_characters_use_case(
    repository: StudioCharactersRepository = Depends(get_studio_characters_repository),
) -> StudioCharactersUseCase:
    return StudioCharactersInteractor(repository=repository)
