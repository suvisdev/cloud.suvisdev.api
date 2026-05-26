import logging

from sqlalchemy import select

from database import get_secom_session_factory
from secom.app.models.role import UserRole
from secom.app.models.user_model import User
from secom.app.repositories.member_repository import MemberRepository
from secom.app.security import hash_password
from secom.app.seed_groups import seed_groups_if_empty

logger = logging.getLogger(__name__)


async def seed_secom_if_empty() -> None:
    """groups·기본 admin/user 계정·members 프로필 시드."""
    await seed_groups_if_empty()

    factory = get_secom_session_factory()
    async with factory() as session:
        result = await session.execute(select(User.id).limit(1))
        if result.scalar_one_or_none() is not None:
            return

        new_users: list[tuple[int, str]] = []
        for username, password, nickname, email, role in (
            ("admin", "admin123", "관리자", "admin@suvis.dev", UserRole.ADMIN),
            ("user", "user123", "일반회원", "user@suvis.dev", UserRole.USER),
        ):
            user = User(
                role=role,
                username=username,
                password_hash=hash_password(password),
                nickname=nickname,
                email=email,
            )
            session.add(user)
            await session.flush()
            new_users.append((user.id, role))
        await session.commit()
        logger.info("[secom.seed] 기본 회원 계정 생성 완료")

    member_repo = MemberRepository()
    for user_id, role in new_users:
        await member_repo.create_for_user(
            user_id,
            gender="undisclosed",
            age_group="30s" if role == UserRole.USER else "40s",
            preferred_genres=["드라마", "SF"] if role == UserRole.USER else [],
            user_role=role,
        )
