from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IsidorBedRepository(ABC):
    """Isidor 침대 조회 아웃바운드 포트 (ABC)."""

    @abstractmethod
    async def get_bed(request: dict[str, Any]) -> int:
        pass
