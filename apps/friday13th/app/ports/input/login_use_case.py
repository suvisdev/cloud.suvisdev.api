from __future__ import annotations

from abc import ABC, abstractmethod

from friday13th.adapter.inbound.api.schemas.login_schema import LoginSchema


class LoginUseCase(ABC):
    """Friday13th 로그인(POST) 입력 포트 (ABC)."""

    @abstractmethod
    async def login(self, payload: LoginSchema) -> int:
        pass
