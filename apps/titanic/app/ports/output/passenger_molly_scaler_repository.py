from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class MollyScalerRepository(ABC):
    """passenger_molly_scaler output port."""

    @abstractmethod
    async def get_scaler(self, request: dict[str, Any]) -> int:
        pass
