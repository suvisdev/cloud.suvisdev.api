from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.passenger_ruth_validation_dto import RuthValidationQuery


class RuthValidationRepository(ABC):
    """passenger_ruth_validation output port."""

    @abstractmethod
    def introduce_myself(self, query: RuthValidationQuery):
        pass
