from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PassengerJackTrainerSchema(BaseModel):
    """passenger_jack_trainer schema (extend later)."""

    model_config = ConfigDict(extra="allow")
