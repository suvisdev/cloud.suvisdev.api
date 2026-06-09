from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.grid_oracle_database_manager import get_db
from fastapi import Depends

from mova.adapter.outbound.pg.characters_pg_repository import CharactersPgRepository
from mova.app.ports.input.characters_use_case import CharactersUseCase
from mova.app.ports.output.characters_repository import CharactersRepository
from mova.app.use_cases.characters_interactor import CharactersInteractor


def get_characters_use_case(db: AsyncSession = Depends(get_db)) -> CharactersUseCase:
    repository: CharactersRepository = CharactersPgRepository(session=db)
    return CharactersInteractor(repository=repository)
