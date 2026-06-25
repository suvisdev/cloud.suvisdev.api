import httpx

from star_craft.app.ports.output.event_publisher_port import EventPublisherPort
from star_craft.domain.events.base_event import BaseEvent


class N8nEventPublisher(EventPublisherPort):

    def __init__(self, webhook_url: str) -> None:
        self._webhook_url = webhook_url

    async def emit(self, event: BaseEvent) -> bool:
        payload = {
            "event_type": type(event).__name__,
            "source_spoke": event.source_spoke,
            "event_id": event.event_id,
            "occurred_at": event.occurred_at.isoformat(),
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self._webhook_url, json=payload)
                return response.status_code == 200
            except Exception:
                return False
