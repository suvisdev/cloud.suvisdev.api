from enum import StrEnum


class UserRole(StrEnum):
    """회원 역할 — `users.role` 컬럼 값 (admin / user)."""

    ADMIN = "admin"
    USER = "user"
