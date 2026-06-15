from __future__ import annotations

from abc import ABC, abstractmethod

from mova.app.dtos.studio_characters_dto import StudioCharactersQuery, StudioCharactersResponse


class StudioCharactersRepository(ABC):

    @abstractmethod
    async def introduce_myself(self, query: StudioCharactersQuery) -> StudioCharactersResponse:
        pass
