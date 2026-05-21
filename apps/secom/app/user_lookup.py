"""Mova 도메인에서 Secom 회원(users) 조회."""

from sqlalchemy import select

from database import get_secom_session_factory
from secom.app.models.user_model import User


async def secom_user_exists(user_id: int) -> bool:
    factory = get_secom_session_factory()
    async with factory() as session:
        return await session.get(User, user_id) is not None


async def get_secom_user_nickname(user_id: int) -> str | None:
    factory = get_secom_session_factory()
    async with factory() as session:
        user = await session.get(User, user_id)
        return user.nickname if user else None


async def get_secom_user_nicknames(user_ids: set[int]) -> dict[int, str]:
    if not user_ids:
        return {}
    factory = get_secom_session_factory()
    async with factory() as session:
        result = await session.execute(
            select(User.id, User.nickname).where(User.id.in_(user_ids)),
        )
        return {row[0]: row[1] for row in result.all()}


async def get_secom_user_profile(user_id: int) -> dict | None:
    """Mova AI 채팅용 — Secom 회원 닉네임만 반영 (preferred_genres 없음)."""
    factory = get_secom_session_factory()
    async with factory() as session:
        user = await session.get(User, user_id)
        if user is None:
            return None
        return {
            "id": user.id,
            "nickname": user.nickname,
            "email": user.email,
            "preferred_genres": [],
        }
