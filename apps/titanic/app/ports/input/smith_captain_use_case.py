from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class SmithCaptainUseCase(ABC):
    """Smith 선장(GET /titanic/captain/captain) 입력 포트 (ABC)."""

    @abstractmethod
    async def get_captain(request: dict[str, Any]) -> int:
        pass
