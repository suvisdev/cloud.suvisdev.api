from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.passenger_isidor_couple_dto import IsidorCoupleQuery


class IsidorCoupleRepository(ABC):
    """passenger_isidor_couple output port."""

    @abstractmethod
    def introduce_myself(self, query: IsidorCoupleQuery):
        pass
