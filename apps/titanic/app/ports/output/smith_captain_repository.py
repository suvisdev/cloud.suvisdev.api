from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class SmithCaptainRepository(ABC):
    """Smith 선장 조회 아웃바운드 포트 (ABC)."""

    @abstractmethod
    async def get_captain(request: dict[str, Any]) -> int:
        pass
