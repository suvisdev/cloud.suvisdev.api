from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LoginUseCase(ABC):
    """Friday13th 로그인(POST) 입력 포트 (ABC)."""

    @abstractmethod
    async def login(payload: dict[str, Any]) -> int:
        pass
