from enum import StrEnum


class UserRole(StrEnum):
    """비즈니스 역할 코드 — PK가 아닌 `user_groups.code` 와 매핑."""

    ADMIN = "admin"
    USER = "user"
