from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AndrewsBlueprintRepository(ABC):
    """crew_andrews_architect output port."""

    @abstractmethod
    async def get_blueprint(self, request: dict[str, Any]) -> int:
        pass
