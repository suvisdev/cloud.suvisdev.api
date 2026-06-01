from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IsidorBedUseCase(ABC):
    """Isidor 침대(GET /titanic/bed/bed) 입력 포트 (ABC)."""

    @abstractmethod
    async def get_bed(request: dict[str, Any]) -> int:
        pass
