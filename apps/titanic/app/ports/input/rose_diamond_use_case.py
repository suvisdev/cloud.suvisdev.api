from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class RoseDiamondUseCase(ABC):
    """Rose 다이아몬드(GET /titanic/diamond/diamond) 입력 포트 (ABC)."""

    @abstractmethod
    async def get_diamond(request: dict[str, Any]) -> int:
        pass
