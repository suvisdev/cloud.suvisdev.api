from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PassengerIsidorCoupleSchema(BaseModel):
    """passenger_isidor_couple schema (extend later)."""

    model_config = ConfigDict(extra="allow")
