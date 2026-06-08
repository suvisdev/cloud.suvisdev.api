from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class RoseDiamondRepository(ABC):
    """passenger_rose_model output port."""

    @abstractmethod
    async def get_diamond(self, request: dict[str, Any]) -> int:
        pass
