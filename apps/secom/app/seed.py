import logging

from sqlalchemy import select

from database import get_secom_session_factory
from secom.app.models.role import UserRole
from secom.app.models.user_group_model import UserGroup
from secom.app.models.user_model import User
from secom.app.security import hash_password

logger = logging.getLogger(__name__)

DEFAULT_GROUPS: list[tuple[str, str]] = [
    (UserRole.ADMIN, "관리자"),
    (UserRole.USER, "일반 회원"),
]


async def seed_secom_if_empty() -> None:
    """권한 그룹·기본 admin/user 계정이 없으면 생성."""
    factory = get_secom_session_factory()
    async with factory() as session:
        result = await session.execute(select(UserGroup.id).limit(1))
        if result.scalar_one_or_none() is not None:
            return

        groups: dict[str, UserGroup] = {}
        for code, label in DEFAULT_GROUPS:
            group = UserGroup(code=code, label=label)
            session.add(group)
            groups[code] = group
        await session.flush()

        for username, password, nickname, email, role in (
            ("admin", "admin123", "관리자", "admin@suvis.dev", UserRole.ADMIN),
            ("user", "user123", "일반회원", "user@suvis.dev", UserRole.USER),
        ):
            session.add(
                User(
                    user_group_id=groups[role].id,
                    username=username,
                    password_hash=hash_password(password),
                    nickname=nickname,
                    email=email,
                ),
            )
        await session.commit()
        logger.info("[secom.seed] user_groups 및 기본 계정 생성 완료")
