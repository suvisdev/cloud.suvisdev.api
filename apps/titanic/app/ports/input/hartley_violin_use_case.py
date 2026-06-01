from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class HartleyViolinUseCase(ABC):
    """Hartley 바이올린(GET /titanic/violin/violin) 입력 포트 (ABC)."""

    @abstractmethod
    async def get_violin(request: dict[str, Any]) -> int:
        pass
