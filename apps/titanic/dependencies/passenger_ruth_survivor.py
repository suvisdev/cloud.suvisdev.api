from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.oracle_database import get_db
from fastapi import Depends

from titanic.adapter.outbound.pg.passenger_ruth_survivor_pg_repository import RuthCorsetPgRepository
from titanic.app.ports.input.passenger_ruth_survivor_use_case import RuthCorsetUseCase
from titanic.app.ports.output.passenger_ruth_survivor_repository import RuthCorsetRepository
from titanic.app.use_cases.passenger_ruth_survivor_interactor import RuthCorsetInteractor


def get_passenger_ruth_survivor_use_case(db: AsyncSession = Depends(get_db)) -> RuthCorsetUseCase:
    repository: RuthCorsetRepository = RuthCorsetPgRepository(session=db)
    return RuthCorsetInteractor(repository=repository)
