from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class RuthCorsetUseCase(ABC):
    """Ruth 코르셋(GET /titanic/corset/corset) 입력 포트 (ABC)."""

    @abstractmethod
    async def get_corset(request: dict[str, Any]) -> int:
        pass
