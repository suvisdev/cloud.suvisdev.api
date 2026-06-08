from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CalPistolUseCase(ABC):
    """passenger_cal_tester input port."""

    @abstractmethod
    async def get_pistol(self, request: dict[str, Any]) -> None:
        pass
