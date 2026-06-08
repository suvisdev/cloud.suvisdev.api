from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class RoseDiamondUseCase(ABC):
    """passenger_rose_model input port."""

    @abstractmethod
    async def get_diamond(self, request: dict[str, Any]) -> int:
        pass
