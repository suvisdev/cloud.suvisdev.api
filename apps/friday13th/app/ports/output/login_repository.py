from __future__ import annotations

from abc import ABC, abstractmethod

from friday13th.app.schemas.auth_schema import LoginSchema


class LoginRepository(ABC):
    """Friday13th 로그인 출력 포트 (ABC)."""

    @abstractmethod
    async def login_user(payload: dict[str, Any]) -> int:
        pass
