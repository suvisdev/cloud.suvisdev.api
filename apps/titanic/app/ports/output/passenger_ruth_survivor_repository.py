from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class RuthCorsetRepository(ABC):
    """passenger_ruth_survivor output port."""

    @abstractmethod
    async def get_corset(self, request: dict[str, Any]) -> int:
        pass
