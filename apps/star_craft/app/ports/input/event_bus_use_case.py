from abc import ABC, abstractmethod

from star_craft.domain.events.base_event import BaseEvent


class EventBusUseCase(ABC):

    @abstractmethod
    async def publish(self, event: BaseEvent) -> None:
        """Spoke가 Hub에 이벤트를 발행한다."""

    @abstractmethod
    async def get_recent_events(self, limit: int = 20) -> list[BaseEvent]:
        """하네스 평가용 — 최근 이벤트 조회."""
