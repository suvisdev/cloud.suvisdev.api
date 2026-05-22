import logging

from sqlalchemy import select

from database import get_secom_session_factory
from secom.app.models.role import UserRole
from secom.app.models.user_model import User
from secom.app.security import hash_password

logger = logging.getLogger(__name__)


async def seed_secom_if_empty() -> None:
    """기본 admin/user 계정이 없으면 생성."""
    factory = get_secom_session_factory()
    async with factory() as session:
        result = await session.execute(select(User.id).limit(1))
        if result.scalar_one_or_none() is not None:
            return

        for username, password, nickname, email, role in (
            ("admin", "admin123", "관리자", "admin@suvis.dev", UserRole.ADMIN),
            ("user", "user123", "일반회원", "user@suvis.dev", UserRole.USER),
        ):
            session.add(
                User(
                    role=role,
                    username=username,
                    password_hash=hash_password(password),
                    nickname=nickname,
                    email=email,
                ),
            )
        await session.commit()
        logger.info("[secom.seed] 기본 회원 계정 생성 완료")
