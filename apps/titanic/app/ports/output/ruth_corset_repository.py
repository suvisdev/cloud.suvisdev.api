from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class RuthCorsetRepository(ABC):
    """Ruth 코르셋 조회 아웃바운드 포트 (ABC)."""

    @abstractmethod
    async def get_corset(request: dict[str, Any]) -> int:
        pass
