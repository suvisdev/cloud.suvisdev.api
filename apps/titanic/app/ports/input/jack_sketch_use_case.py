from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class JackSketchUseCase(ABC):
    """Jack 스케치(GET /titanic/sketch/sketch) 입력 포트 (ABC)."""

    @abstractmethod
    async def get_sketch(request: dict[str, Any]) -> int:
        pass
