"""회원 ↔ 그룹 N:M — `member_groups`."""

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from friday13th.app.models.base import SecomModel


class MemberGroup(SecomModel):
    """한 회원이 여러 그룹에 속할 수 있음. PK `id`, UNIQUE (member_id, group_id)."""

    __tablename__ = "member_groups"
    __table_args__ = (
        UniqueConstraint("member_id", "group_id", name="uq_member_groups_member_group"),
    )

    member_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("members.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    group_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
