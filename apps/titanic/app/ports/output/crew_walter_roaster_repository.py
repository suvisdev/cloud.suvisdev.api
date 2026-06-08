from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.crew_walter_roaster_dto import WalterQuery


class WalterRepository(ABC):
    """Walter 소개 출력 포트 (ABC)."""

    @abstractmethod
    def introduce_myself(self, query: WalterQuery) -> None:
        pass
