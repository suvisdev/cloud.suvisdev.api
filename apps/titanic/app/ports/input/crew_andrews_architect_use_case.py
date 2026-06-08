from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from titanic.adapter.inbound.api.schemas.crew_andrews_architect_schema import (
        AndrewsArchitectSchema,
    )


class AndrewsArchitectUseCase(ABC):
    """AndrewsArchitect input port."""

    @abstractmethod
    async def introduce_myself(
        self,
        schemas: "AndrewsArchitectSchema | None" = None,
    ):
        pass
