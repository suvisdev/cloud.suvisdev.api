from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.passenger_rose_model_dto import RoseModelQuery


class RoseModelRepository(ABC):
    """passenger_rose_model output port."""

    @abstractmethod
    def introduce_myself(self, query: RoseModelQuery):
        pass
