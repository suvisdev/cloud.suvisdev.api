import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from database import get_secom_session_factory
from secom.app.models.role import UserRole
from secom.app.models.user_group_model import UserGroup
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
    async def _get_group_by_role(self, session, role_code: str) -> UserGroup:
        normalized = role_code.strip().lower()
        if normalized not in {UserRole.ADMIN, UserRole.USER}:
            raise UserRepositoryError("유효하지 않은 역할입니다.", status_code=400)
        result = await session.execute(
            select(UserGroup).where(UserGroup.code == normalized),
        )
        group = result.scalar_one_or_none()
        if group is None:
            raise UserRepositoryError(
                "권한 그룹이 없습니다. 서버 시드를 실행해 주세요.",
                status_code=503,
            )
        return group

    async def save_user(self, user_schema: UserSchema) -> int:
        logger.info(
            "[UserRepository] save_user 진입 (Neon) — %s",
            user_schema.log_summary(),
        )
        factory = get_secom_session_factory()
        async with factory() as session:
            existing = await session.execute(
                select(User.id).where(User.username == user_schema.username),
            )
            if existing.scalar_one_or_none() is not None:
                raise UserRepositoryError("이미 사용 중인 아이디입니다.", status_code=409)

            group = await self._get_group_by_role(session, user_schema.role)
            user = User(
                user_group_id=group.id,
                username=user_schema.username,
                password_hash=hash_password(user_schema.password),
                nickname=user_schema.nickname,
                email=user_schema.email,
            )
            session.add(user)
            try:
                await session.commit()
                await session.refresh(user)
            except IntegrityError as e:
                await session.rollback()
                raise UserRepositoryError("이미 사용 중인 아이디입니다.", status_code=409) from e
            return user.id

    async def login_user(self, login_schema: LoginSchema) -> int:
        logger.info(
            "[UserRepository] login_user 진입 (Neon) — %s",
            login_schema.log_summary(),
        )
        factory = get_secom_session_factory()
        async with factory() as session:
            result = await session.execute(
                select(User)
                .options(selectinload(User.user_group))
                .where(User.username == login_schema.username),
            )
            user = result.scalar_one_or_none()
            if user is None or not verify_password(login_schema.password, user.password_hash):
                raise UserRepositoryError(
                    "아이디 또는 비밀번호가 올바르지 않습니다.",
                    status_code=401,
                )
            return user.id
