from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.oracle_database import get_db
from fastapi import Depends

from mova.adapter.outbound.pg.tags_pg_repository import TagsPgRepository
from mova.app.ports.input.tags_use_case import TagsUseCase
from mova.app.ports.output.tags_repository import TagsRepository
from mova.app.use_cases.tags_interactor import TagsInteractor


def get_tags_use_case(db: AsyncSession = Depends(get_db)) -> TagsUseCase:
    repository: TagsRepository = TagsPgRepository(session=db)
    return TagsInteractor(repository=repository)
