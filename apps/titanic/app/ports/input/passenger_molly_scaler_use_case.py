from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class MollyScalerUseCase(ABC):
    """passenger_molly_scaler input port."""

    @abstractmethod
    async def get_scaler(self, request: dict[str, Any]) -> int:
        pass
