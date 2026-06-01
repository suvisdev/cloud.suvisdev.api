from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CalPistolUseCase(ABC):
    """Cal 권총(GET /titanic/pistol/pistol) 입력 포트 (ABC)."""

    @abstractmethod
    async def get_pistol(request: dict[str, Any]) -> None:
        pass
