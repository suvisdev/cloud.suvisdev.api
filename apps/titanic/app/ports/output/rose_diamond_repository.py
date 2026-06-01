from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class RoseDiamondRepository(ABC):
    """Rose 다이아몬드 조회 아웃바운드 포트 (ABC)."""

    @abstractmethod
    async def get_diamond(request: dict[str, Any]) -> int:
        pass
