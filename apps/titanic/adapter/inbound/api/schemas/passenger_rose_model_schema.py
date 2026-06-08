from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PassengerRoseModelSchema(BaseModel):
    """passenger_rose_model schema (extend later)."""

    model_config = ConfigDict(extra="allow")
