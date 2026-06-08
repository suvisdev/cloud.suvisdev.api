from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.passenger_jack_trainer_dto import JackTrainerQuery
from titanic.app.dtos.passenger_jack_trainer_dto import JackTrainerResponse

class JackTrainerRepository(ABC):
    """passenger_jack_trainer output port."""

    @abstractmethod
    def introduce_myself(self, query: JackTrainerQuery)->JackTrainerResponse:
        pass
