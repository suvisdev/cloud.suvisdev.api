from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from secom.app.models.base import SecomModel


class UserGroup(SecomModel):
    """회원 권한 그룹 (admin / user). PK는 `id`, 식별은 `code` UNIQUE."""

    __tablename__ = "user_groups"

    code: Mapped[str] = mapped_column(String(16), unique=True, nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(32), nullable=False)

    users: Mapped[list["User"]] = relationship(back_populates="user_group")
