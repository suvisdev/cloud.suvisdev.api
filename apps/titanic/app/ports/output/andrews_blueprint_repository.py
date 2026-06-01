from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AndrewsBlueprintRepository(ABC):
    """Andrews 설계도 조회 아웃바운드 포트 (ABC)."""

    @abstractmethod
    async def get_blueprint(request: dict[str, Any]) -> int:
        pass
