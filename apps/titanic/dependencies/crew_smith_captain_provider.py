from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.grid_oracle_database_manager import get_db
from fastapi import Depends

from titanic.adapter.outbound.pg.crew_smith_captain_pg_repository import SmithCaptainPgRepository
from titanic.app.ports.input.crew_smith_captain_use_case import SmithCaptainUseCase
from titanic.app.ports.input.crew_walter_roaster_use_case import WalterUseCase
from titanic.app.ports.input.passenger_cal_tester_use_case import CalTesterUseCase
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.input.passenger_rose_model_use_case import RoseModelUseCase
from titanic.app.ports.output.crew_smith_captain_repository import SmithCaptainRepository
from titanic.app.use_cases.crew_smith_captain_interactor import SmithCaptainInteractor
from titanic.dependencies.crew_walter_roaster_provider import get_walter_roaster_use_case
from titanic.dependencies.passenger_cal_tester_provider import get_cal_tester_use_case
from titanic.dependencies.passenger_jack_trainer_provider import get_jack_trainer_use_case
from titanic.dependencies.passenger_rose_model_provider import get_rose_model_use_case


def get_smith_captain_repository(
        db: AsyncSession = Depends(get_db)
) -> SmithCaptainRepository:
    return SmithCaptainPgRepository(session=db)

def get_smith_captain_use_case(
        repository: SmithCaptainRepository = Depends(get_smith_captain_repository),
        jack: JackTrainerUseCase = Depends(get_jack_trainer_use_case),
        rose: RoseModelUseCase = Depends(get_rose_model_use_case),
        cal: CalTesterUseCase = Depends(get_cal_tester_use_case),
        walter: WalterUseCase = Depends(get_walter_roaster_use_case),
) -> SmithCaptainUseCase:
    return SmithCaptainInteractor(repository=repository)
