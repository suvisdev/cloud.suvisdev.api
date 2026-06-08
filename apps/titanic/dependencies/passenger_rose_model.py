from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.oracle_database import get_db
from fastapi import Depends

from titanic.adapter.outbound.pg.passenger_rose_model_pg_repository import RoseDiamondPgRepository
from titanic.app.ports.input.passenger_rose_model_use_case import RoseDiamondUseCase
from titanic.app.ports.output.passenger_rose_model_repository import RoseDiamondRepository
from titanic.app.use_cases.passenger_rose_model_interactor import RoseDiamondInteractor


def get_passenger_rose_model_use_case(db: AsyncSession = Depends(get_db)) -> RoseDiamondUseCase:
    repository: RoseDiamondRepository = RoseDiamondPgRepository(session=db)
    return RoseDiamondInteractor(repository=repository)
