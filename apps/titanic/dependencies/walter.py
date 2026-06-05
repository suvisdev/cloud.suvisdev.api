from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.oracle_database import get_db
from fastapi import Depends

"""
Walter 의존성 조립소 (DIP 팩토리).

DIP 원칙:
  - 라우터는 구현체(WalterPgRepository)를 직접 알지 못한다.
  - 리턴 타입은 구현체가 아닌 포트(WalterUseCase)로 선언한다.
  - 세션은 core 의 get_db 에서 주입받는다 (AsyncSession).
"""

from titanic.app.ports.input.walter_use_case import WalterUseCase
from titanic.app.use_cases.walter_interactor import WalterInteractor
from titanic.adapter.outbound.pg.walter_pg_repository import WalterPgRepository
from titanic.app.ports.output.walter_repository import WalterRepository

def get_walter_use_case(db: AsyncSession = Depends(get_db)) -> WalterUseCase:
    repository: WalterRepository = WalterPgRepository(session=db)
    return WalterInteractor(repository=repository)
