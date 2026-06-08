from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.crew_andrews_architect_dto import AndrewsArchitectQuery
from titanic.app.dtos.crew_andrews_architect_dto import AndrewsArchitectResponse

class AndrewsArchitectRepository(ABC):
    """crew_andrews_architect output port."""

    @abstractmethod
    def introduce_myself(self, query: AndrewsArchitectQuery)->AndrewsArchitectResponse:
        pass
