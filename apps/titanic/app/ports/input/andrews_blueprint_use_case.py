from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AndrewsBlueprintUseCase(ABC):
    """Andrews 설계도(GET /titanic/andrews/blueprint) 입력 포트 (ABC)."""

    @abstractmethod
    async def get_blueprint(request: dict[str, Any]) -> int:
        pass
