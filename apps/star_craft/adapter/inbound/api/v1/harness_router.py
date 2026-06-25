from fastapi import APIRouter, Depends

from star_craft.adapter.inbound.api.schemas.event_schema import EventResponse
from star_craft.app.dtos.event_dto import EventDto
from star_craft.app.ports.input.event_bus_use_case import EventBusUseCase
from star_craft.dependencies.providers import get_event_bus

harness_router = APIRouter(prefix="/star-craft", tags=["star-craft"])


@harness_router.get("/events", response_model=list[EventResponse])
async def get_recent_events(
    limit: int = 20,
    bus: EventBusUseCase = Depends(get_event_bus),
) -> list[EventResponse]:
    events = await bus.get_recent_events(limit=limit)
    dtos = [EventDto.from_event(e) for e in events]
    return [EventResponse(**dto.__dict__) for dto in dtos]
