from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AndrewsBlueprintUseCase(ABC):
    """crew_andrews_architect input port."""

    @abstractmethod
    async def get_blueprint(self, request: dict[str, Any]) -> int:
        pass
