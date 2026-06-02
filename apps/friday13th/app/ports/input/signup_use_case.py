from __future__ import annotations

from abc import ABC, abstractmethod

from friday13th.adapter.inbound.api.schemas.signup_schema import SignupSchema


class SignupUseCase(ABC):
    """Friday13th 회원가입(POST) 입력 포트 (ABC)."""

    @abstractmethod
    async def signup(self, payload: SignupSchema) -> int:
        pass
