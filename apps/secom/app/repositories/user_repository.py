import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database import get_session_factory
from secom.app.models.user_model import User
from secom.app.schemas.auth_schema import LoginSchema, UserSchema
from secom.app.security import hash_password, verify_password

logger = logging.getLogger(__name__)


class UserRepositoryError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class UserRepository:
    async def save_user(self, user_schema: UserSchema) -> None:
        logger.info(
            "[UserRepository] save_user 진입 (Neon) — %s",
            user_schema.log_summary(),
        )
        factory = get_session_factory()
        async with factory() as session:
            existing = await session.execute(
                select(User).where(User.username == user_schema.username),
            )
            if existing.scalar_one_or_none() is not None:
                raise UserRepositoryError("이미 사용 중인 아이디입니다.", status_code=409)

            user = User(
                username=user_schema.username,
                password_hash=hash_password(user_schema.password),
                nickname=user_schema.nickname,
                email=user_schema.email,
                role=user_schema.role,
            )
            session.add(user)
            try:
                await session.commit()
            except IntegrityError as e:
                await session.rollback()
                raise UserRepositoryError("이미 사용 중인 아이디입니다.", status_code=409) from e

    async def login_user(self, login_schema: LoginSchema) -> None:
        logger.info(
            "[UserRepository] login_user 진입 (Neon) — %s",
            login_schema.log_summary(),
        )
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(
                select(User).where(User.username == login_schema.username),
            )
            user = result.scalar_one_or_none()
            if user is None or not verify_password(login_schema.password, user.password_hash):
                raise UserRepositoryError(
                    "아이디 또는 비밀번호가 올바르지 않습니다.",
                    status_code=401,
                )
