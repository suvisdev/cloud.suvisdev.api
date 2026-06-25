from datetime import datetime

from pydantic import BaseModel


class EventResponse(BaseModel):
    event_id: str
    event_type: str
    source_spoke: str
    occurred_at: datetime
