from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.oracle_database import get_secom_db
from fastapi import Depends

from viewer.adapter.outbound.pg.signup_pg_repository import SignupPgRepository, SignupRepositoryError
from viewer.app.ports.input.signup_use_case import SignupUseCase
from viewer.app.ports.output.signup_repository import SignupRepository
from viewer.app.use_cases.signup_interactor import SignupInteractor


def get_signup_use_case(db: AsyncSession = Depends(get_secom_db)) -> SignupUseCase:
    repository: SignupRepository = SignupPgRepository(session=db)
    return SignupInteractor(repository=repository)


__all__ = ["SignupRepositoryError", "get_signup_use_case"]
