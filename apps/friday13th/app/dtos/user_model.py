from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from friday13th.app.dtos.base import SecomModel
from friday13th.app.dtos.role import UserRole


class User(SecomModel):
    """회원. PK `id` — 로그인·API 식별은 `username` UNIQUE."""

    __tablename__ = "users"

    role: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=UserRole.USER,
        index=True,
    )
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


async def secom_user_exists(user_id: int) -> bool:
    from sqlalchemy import select

    from core.database import get_secom_session_factory

    factory = get_secom_session_factory()
    async with factory() as session:
        result = await session.execute(select(User.id).where(User.id == user_id))
        return result.scalar_one_or_none() is not None


async def get_secom_user_nicknames(user_ids: set[int]) -> dict[int, str]:
    if not user_ids:
        return {}

    from sqlalchemy import select

    from core.database import get_secom_session_factory

    factory = get_secom_session_factory()
    async with factory() as session:
        result = await session.execute(
            select(User.id, User.nickname).where(User.id.in_(user_ids)),
        )
        return {row.id: row.nickname for row in result.all()}


async def get_secom_user_profile(user_id: int) -> dict:
    from sqlalchemy import select

    from core.database import get_secom_session_factory
    from friday13th.app.dtos.member_model import Member

    factory = get_secom_session_factory()
    async with factory() as session:
        user = (
            await session.execute(select(User).where(User.id == user_id))
        ).scalar_one_or_none()
        if user is None:
            raise ValueError(f"회원 ID {user_id}를 찾을 수 없습니다.")

        member = (
            await session.execute(select(Member).where(Member.user_id == user_id))
        ).scalar_one_or_none()

        return {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "email": user.email,
            "preferred_genres": list(member.preferred_genres) if member else [],
            "gender": member.gender if member else "undisclosed",
            "age_group": member.age_group if member else "undisclosed",
        }


async def seed_secom_if_empty() -> None:
    """Mova/Secom 호환 — users 테이블 시드는 별도 스크립트에서 수행."""
    return None
