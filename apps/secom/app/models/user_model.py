from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from secom.app.models.base import SecomModel
from secom.app.models.role import UserRole


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
