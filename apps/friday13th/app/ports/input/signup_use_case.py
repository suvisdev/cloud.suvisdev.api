from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class SignupUseCase(ABC):
    """Friday13th 회원가입(POST) 입력 포트 (ABC)."""

    @abstractmethod
    async def signup(payload: dict[str, Any]) -> int:
        pass
