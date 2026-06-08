from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.oracle_database import get_db
from fastapi import Depends

from titanic.adapter.outbound.pg.passenger_cal_tester_pg_repository import CalPistolPgRepository
from titanic.app.ports.input.passenger_cal_tester_use_case import CalPistolUseCase
from titanic.app.ports.output.passenger_cal_tester_repository import CalPistolRepository
from titanic.app.use_cases.passenger_cal_tester_interactor import CalPistolInteractor


def get_passenger_cal_tester_use_case(db: AsyncSession = Depends(get_db)) -> CalPistolUseCase:
    repository: CalPistolRepository = CalPistolPgRepository(session=db)
    return CalPistolInteractor(repository=repository)
