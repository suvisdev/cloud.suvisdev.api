from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.oracle_database import get_db
from fastapi import Depends

from titanic.adapter.outbound.pg.passenger_jack_trainer_pg_repository import JackSketchPgRepository
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackSketchUseCase
from titanic.app.ports.output.passenger_jack_trainer_repository import JackSketchRepository
from titanic.app.use_cases.passenger_jack_trainer_interactor import JackSketchInteractor


def get_passenger_jack_trainer_use_case(db: AsyncSession = Depends(get_db)) -> JackSketchUseCase:
    repository: JackSketchRepository = JackSketchPgRepository(session=db)
    return JackSketchInteractor(repository=repository)
