from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PassengerRuthSurvivorSchema(BaseModel):
    """passenger_ruth_survivor schema (extend later)."""

    model_config = ConfigDict(extra="allow")
