import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from core.database import get_secom_session_factory
from friday13th.app.models.role import UserRole
from friday13th.app.models.user_model import User
from friday13th.app.repositories.member_repository import MemberRepository
from friday13th.app.schemas.auth_schema import LoginSchema, UserSchema
from friday13th.app.security import hash_password, verify_password

logger = logging.getLogger(__name__)


class UserRepositoryError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class UserRepository:
    @staticmethod
    def _normalize_role(role_code: str) -> str:
        normalized = role_code.strip().lower()
        if normalized not in {UserRole.ADMIN, UserRole.USER}:
            raise UserRepositoryError("유효하지 않은 역할입니다.", status_code=400)
        return normalized

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

            role = self._normalize_role(user_schema.role)
            user = User(
                role=role,
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
            user_id = user.id

        try:
            await MemberRepository().create_for_user(
                user_id,
                gender=user_schema.gender,
                age_group=user_schema.age_group,
                birth_year=user_schema.birth_year,
                preferred_genres=user_schema.preferred_genres,
                bio=user_schema.bio,
                user_role=role,
            )
        except Exception:
            logger.exception("[UserRepository] members 프로필 생성 실패 user_id=%s", user_id)
        return user_id

    async def login_user(self, login_schema: LoginSchema) -> int:
        logger.info(
            "[UserRepository] login_user 진입 (Neon) — %s",
            login_schema.log_summary(),
        )
        factory = get_secom_session_factory()
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
            return user.id
