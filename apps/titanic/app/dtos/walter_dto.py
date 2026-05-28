from __future__ import annotations

from pydantic import BaseModel, Field


class WalterPassengerItem(BaseModel):
    id: int
    passenger_id: str
    survived: str
    pclass: str
    name: str
    gender: str
    age: str
    sibsp: str
    parch: str
    ticket: str
    fare: str
    cabin: str
    embarked: str


class WalterPassengerPage(BaseModel):
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1)
    total_count: int = Field(..., ge=0)
    total_pages: int = Field(..., ge=0)
    items: list[WalterPassengerItem]
