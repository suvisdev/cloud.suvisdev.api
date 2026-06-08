from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class JackSketchRepository(ABC):
    """passenger_jack_trainer output port."""

    @abstractmethod
    async def get_sketch(self, request: dict[str, Any]) -> int:
        pass
