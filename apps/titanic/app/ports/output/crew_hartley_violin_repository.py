from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class HartleyViolinRepository(ABC):
    """crew_hartley_violin output port."""

    @abstractmethod
    async def get_violin(self, request: dict[str, Any]) -> int:
        pass
