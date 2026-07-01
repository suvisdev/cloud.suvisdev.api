from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class InboxReceiveSchema(BaseModel):
    sender: str = ""
    subject: str = ""
    body: str = ""


class InboxItemSchema(BaseModel):
    id: int
    sender: str
    subject: str
    body: str
    received_at: datetime
