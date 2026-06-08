from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class SmithCaptainRepository(ABC):
    """crew_smith_captain output port."""

    @abstractmethod
    async def get_captain(self, request: dict[str, Any]) -> int:
        pass
