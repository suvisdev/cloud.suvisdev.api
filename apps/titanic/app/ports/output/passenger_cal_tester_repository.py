from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CalPistolRepository(ABC):
    """passenger_cal_tester output port."""

    @abstractmethod
    async def get_pistol(self, request: dict[str, Any]) -> None:
        pass
