from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IsidorBedRepository(ABC):
    """passenger_isidor_couple output port."""

    @abstractmethod
    async def get_bed(self, request: dict[str, Any]) -> int:
        pass
