from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class HartleyViolinUseCase(ABC):
    """crew_hartley_violin input port."""

    @abstractmethod
    async def get_violin(self, request: dict[str, Any]) -> int:
        pass
