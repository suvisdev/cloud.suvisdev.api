from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PassengerMollyScalerSchema(BaseModel):
    """passenger_molly_scaler schema (extend later)."""

    model_config = ConfigDict(extra="allow")
