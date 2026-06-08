from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.crew_lowe_boat_dto import LoweBoatQuery


class LoweBoatRepository(ABC):
    """crew_lowe_boat output port."""

    @abstractmethod
    def introduce_myself(self, query: LoweBoatQuery):
        pass
