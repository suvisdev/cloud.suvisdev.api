from star_craft.app.dtos.event_dto import EventDto
from star_craft.app.ports.input.event_bus_use_case import EventBusUseCase
from star_craft.app.ports.output.event_publisher_port import EventPublisherPort
from star_craft.domain.events.base_event import BaseEvent


class EventBusInteractor(EventBusUseCase):

    def __init__(self, publisher: EventPublisherPort) -> None:
        self._publisher = publisher
        self._store: list[BaseEvent] = []

    async def publish(self, event: BaseEvent) -> None:
        self._store.append(event)
        await self._publisher.emit(event)

    async def get_recent_events(self, limit: int = 20) -> list[BaseEvent]:
        return self._store[-limit:]
