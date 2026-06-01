"""권한 그룹 마스터 — `groups`."""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from friday13th.app.dtos.base import SecomModel


class Group(SecomModel):
    """회원 그룹 (플랫폼·Mova 관리 등). PK `id`, 비즈니스 키 `code`."""

    __tablename__ = "groups"

    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
