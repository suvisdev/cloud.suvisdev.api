from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.grid_oracle_database_manager import get_db
from fastapi import Depends

from mova.adapter.outbound.pg.platform_assistants_pg_repository import PlatformAssistantsPgRepository
from mova.app.ports.input.platform_assistants_use_case import PlatformAssistantsUseCase
from mova.app.ports.output.platform_assistants_repository import PlatformAssistantsRepository
from mova.app.use_cases.platform_assistants_interactor import PlatformAssistantsInteractor


def get_platform_assistants_repository(
    db: AsyncSession = Depends(get_db),
) -> PlatformAssistantsRepository:
    return PlatformAssistantsPgRepository(session=db)


def get_platform_assistants_use_case(
    repository: PlatformAssistantsRepository = Depends(get_platform_assistants_repository),
) -> PlatformAssistantsUseCase:
    return PlatformAssistantsInteractor(repository=repository)
