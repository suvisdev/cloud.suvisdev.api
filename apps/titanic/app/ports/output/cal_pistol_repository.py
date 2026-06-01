from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CalPistolRepository(ABC):
    """Cal 권총 조회 아웃바운드 포트 (ABC)."""

    @abstractmethod
    async def get_pistol(request: dict[str, Any]) -> None:
        pass
