from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class HartleyViolinRepository(ABC):
    """Hartley 바이올린 조회 아웃바운드 포트 (ABC)."""

    @abstractmethod
    async def get_violin(request: dict[str, Any]) -> int:
        pass
