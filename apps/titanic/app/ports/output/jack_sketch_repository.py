from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class JackSketchRepository(ABC):
    """Jack 스케치 조회 아웃바운드 포트 (ABC)."""

    @abstractmethod
    async def get_sketch(request: dict[str, Any]) -> int:
        pass
