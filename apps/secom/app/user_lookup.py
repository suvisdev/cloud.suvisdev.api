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
    """Mova AI 채팅용 — users + members 프로필."""
    from secom.app.models.member_model import Member

    factory = get_secom_session_factory()
    async with factory() as session:
        user = await session.get(User, user_id)
        if user is None:
            return None
        result = await session.execute(
            select(Member).where(Member.user_id == user_id),
        )
        member = result.scalar_one_or_none()
        preferred: list = []
        gender = None
        age_group = None
        member_id = None
        if member is not None:
            member_id = member.id
            preferred = list(member.preferred_genres or [])
            gender = member.gender
            age_group = member.age_group
        return {
            "id": user.id,
            "member_id": member_id,
            "nickname": user.nickname,
            "email": user.email,
            "gender": gender,
            "age_group": age_group,
            "preferred_genres": preferred,
        }
