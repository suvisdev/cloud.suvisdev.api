from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LoweBoatUseCase(ABC):
    """crew_lowe_boat input port."""

    @abstractmethod
    async def get_boat(self, request: dict[str, Any]) -> int:
        pass
