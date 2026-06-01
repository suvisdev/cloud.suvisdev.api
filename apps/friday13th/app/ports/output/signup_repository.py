from __future__ import annotations

from abc import ABC, abstractmethod

from friday13th.app.schemas.auth_schema import UserSchema


class SignupRepository(ABC):
    """Friday13th 회원가입 출력 포트 (ABC)."""

    @abstractmethod
    async def save_user(payload: dict[str, Any]) -> int:
        pass
