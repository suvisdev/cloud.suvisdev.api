from abc import ABC, abstractmethod

from star_craft.domain.events.base_event import BaseEvent


class EventPublisherPort(ABC):

    @abstractmethod
    async def emit(self, event: BaseEvent) -> bool:
        """외부 채널(n8n, Slack 등)로 이벤트를 발행한다."""
