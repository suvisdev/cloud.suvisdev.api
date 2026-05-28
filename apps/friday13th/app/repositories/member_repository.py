import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from core.database import get_secom_session_factory
from friday13th.app.models.group_model import Group
from friday13th.app.models.member_group_model import MemberGroup
from friday13th.app.models.member_model import Member
from friday13th.app.models.member_profile import (
    MEMBER_AGE_GROUPS,
    MEMBER_GENDERS,
    MemberAgeGroup,
    MemberGender,
)
from friday13th.app.models.role import UserRole
from friday13th.app.models.user_model import User

logger = logging.getLogger(__name__)

DEFAULT_GROUP_CODES = ("mova_member",)
ADMIN_EXTRA_GROUPS = ("platform_admin", "mova_admin")


class MemberRepositoryError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class MemberRepository:
    @staticmethod
    def _normalize_gender(value: str | None) -> str:
        g = (value or MemberGender.UNDISCLOSED).strip().lower()
        if g not in MEMBER_GENDERS:
            raise MemberRepositoryError(
                f"gender는 {', '.join(sorted(MEMBER_GENDERS))} 중 하나여야 합니다.",
                status_code=400,
            )
        return g

    @staticmethod
    def _normalize_age_group(value: str | None) -> str:
        a = (value or MemberAgeGroup.UNDISCLOSED).strip().lower()
        if a not in MEMBER_AGE_GROUPS:
            raise MemberRepositoryError(
                f"age_group는 {', '.join(sorted(MEMBER_AGE_GROUPS))} 중 하나여야 합니다.",
                status_code=400,
            )
        return a

    async def get_by_user_id(self, user_id: int) -> Member | None:
        factory = get_secom_session_factory()
        async with factory() as session:
            result = await session.execute(
                select(Member).where(Member.user_id == user_id),
            )
            return result.scalar_one_or_none()

    async def get_by_id(self, member_id: int) -> Member | None:
        factory = get_secom_session_factory()
        async with factory() as session:
            return await session.get(Member, member_id)

    async def _group_by_code(self, session, code: str) -> Group | None:
        result = await session.execute(select(Group).where(Group.code == code))
        return result.scalar_one_or_none()

    async def _attach_groups(
        self,
        session,
        member_id: int,
        codes: tuple[str, ...],
    ) -> None:
        for code in codes:
            group = await self._group_by_code(session, code)
            if group is None:
                logger.warning("[MemberRepository] 그룹 없음 — code=%s", code)
                continue
            exists = await session.execute(
                select(MemberGroup.id).where(
                    MemberGroup.member_id == member_id,
                    MemberGroup.group_id == group.id,
                ),
            )
            if exists.scalar_one_or_none() is not None:
                continue
            session.add(MemberGroup(member_id=member_id, group_id=group.id))

    async def create_for_user(
        self,
        user_id: int,
        *,
        gender: str | None = None,
        age_group: str | None = None,
        birth_year: int | None = None,
        preferred_genres: list[str] | None = None,
        bio: str = "",
        user_role: str = UserRole.USER,
    ) -> Member:
        gender_n = self._normalize_gender(gender)
        age_n = self._normalize_age_group(age_group)
        genres = [str(g).strip() for g in (preferred_genres or []) if str(g).strip()]

        if birth_year is not None and (birth_year < 1900 or birth_year > 2100):
            raise MemberRepositoryError("birth_year가 올바르지 않습니다.", status_code=400)

        factory = get_secom_session_factory()
        async with factory() as session:
            user = await session.get(User, user_id)
            if user is None:
                raise MemberRepositoryError(
                    f"회원 ID {user_id}를 찾을 수 없습니다.",
                    status_code=404,
                )

            result = await session.execute(
                select(Member).where(Member.user_id == user_id),
            )
            row = result.scalar_one_or_none()
            if row is None:
                row = Member(
                    user_id=user_id,
                    gender=gender_n,
                    age_group=age_n,
                    birth_year=birth_year,
                    preferred_genres=genres,
                    bio=(bio or "")[:255],
                )
                session.add(row)
                await session.flush()
            else:
                row.gender = gender_n
                row.age_group = age_n
                row.birth_year = birth_year
                row.preferred_genres = genres
                row.bio = (bio or row.bio or "")[:255]

            group_codes = list(DEFAULT_GROUP_CODES)
            if user_role == UserRole.ADMIN:
                group_codes.extend(ADMIN_EXTRA_GROUPS)
            await self._attach_groups(session, row.id, tuple(group_codes))

            try:
                await session.commit()
                await session.refresh(row)
            except IntegrityError as e:
                await session.rollback()
                raise MemberRepositoryError(
                    "회원 프로필 저장에 실패했습니다.",
                    status_code=409,
                ) from e
            return row

    async def ensure_for_user(self, user_id: int) -> Member:
        existing = await self.get_by_user_id(user_id)
        if existing is not None:
            return existing
        factory = get_secom_session_factory()
        async with factory() as session:
            user = await session.get(User, user_id)
            role = user.role if user else UserRole.USER
        return await self.create_for_user(user_id, user_role=role)
