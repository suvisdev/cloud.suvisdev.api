from __future__ import annotations

from pydantic import BaseModel, Field


class WalterPassengerItem(BaseModel):
    id: int
    passenger_id: str = ""
    survived: str = ""
    pclass: str = ""
    name: str = ""
    gender: str = ""
    age: str = ""
    sibsp: str = ""
    parch: str = ""
    ticket: str = ""
    fare: str = ""
    cabin: str = ""
    embarked: str = ""


class WalterPassengerPage(BaseModel):
    page: int
    page_size: int
    total_count: int
    total_pages: int
    items: list[WalterPassengerItem] = Field(default_factory=list)
