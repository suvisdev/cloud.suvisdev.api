"""회원 상세 프로필 — 로그인 `users` 와 1:1 (`members`)."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from friday13th.app.dtos.base import SecomModel
from friday13th.app.dtos.member_profile import MemberAgeGroup, MemberGender


class Member(SecomModel):
    """Mova·Secom 공용 회원 프로필. 인증은 `users`, 취향·인구통계는 여기."""

    __tablename__ = "members"

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    gender: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=MemberGender.UNDISCLOSED,
        index=True,
    )
    age_group: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=MemberAgeGroup.UNDISCLOSED,
        index=True,
    )
    birth_year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="출생 연도 (선택)",
    )
    preferred_genres: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        comment="선호 장르 배열",
    )
    bio: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class MemberRepository:
    """Mova·Friday13th 공용 members 접근 (구 secom MemberRepository 호환)."""

    async def ensure_for_user(self, user_id: int) -> Member:
        from sqlalchemy import select

        from core.database import get_secom_session_factory

        factory = get_secom_session_factory()
        async with factory() as session:
            member = (
                await session.execute(select(Member).where(Member.user_id == user_id))
            ).scalar_one_or_none()
            if member is not None:
                return member

            member = Member(user_id=user_id)
            session.add(member)
            await session.commit()
            await session.refresh(member)
            return member

    async def create_for_user(
        self,
        user_id: int,
        *,
        gender: str = MemberGender.UNDISCLOSED,
        age_group: str = MemberAgeGroup.UNDISCLOSED,
        birth_year: int | None = None,
        preferred_genres: list | None = None,
        bio: str = "",
        user_role: str | None = None,
    ) -> Member:
        from sqlalchemy import select

        from core.database import get_secom_session_factory

        factory = get_secom_session_factory()
        async with factory() as session:
            existing = (
                await session.execute(select(Member).where(Member.user_id == user_id))
            ).scalar_one_or_none()
            if existing is not None:
                return existing

            member = Member(
                user_id=user_id,
                gender=gender,
                age_group=age_group,
                birth_year=birth_year,
                preferred_genres=preferred_genres or [],
                bio=bio or "",
            )
            session.add(member)
            await session.commit()
            await session.refresh(member)
            return member
