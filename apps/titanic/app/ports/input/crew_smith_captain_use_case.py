from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class SmithCaptainUseCase(ABC):
    """crew_smith_captain input port."""

    @abstractmethod
    async def get_captain(self, request: dict[str, Any]) -> int:
        pass
