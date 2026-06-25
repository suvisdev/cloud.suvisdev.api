import os

from star_craft.adapter.outbound.publisher.n8n_event_publisher import N8nEventPublisher
from star_craft.app.ports.input.event_bus_use_case import EventBusUseCase
from star_craft.app.use_cases.event_bus_interactor import EventBusInteractor

_N8N_URL = os.environ.get("N8N_WEBHOOK_URL", "http://n8n:5678/webhook/b7b20b1a-519a-4465-94fa-c41a450e1ad2")

_bus: EventBusInteractor | None = None


def get_event_bus() -> EventBusUseCase:
    global _bus
    if _bus is None:
        publisher = N8nEventPublisher(webhook_url=_N8N_URL)
        _bus = EventBusInteractor(publisher=publisher)
    return _bus
