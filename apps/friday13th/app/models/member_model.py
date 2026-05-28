"""회원 상세 프로필 — 로그인 `users` 와 1:1 (`members`)."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from friday13th.app.models.base import SecomModel
from friday13th.app.models.member_profile import MemberAgeGroup, MemberGender


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
