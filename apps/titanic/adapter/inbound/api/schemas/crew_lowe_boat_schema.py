from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CrewLoweBoatSchema(BaseModel):
    """crew_lowe_boat schema (extend later)."""

    model_config = ConfigDict(extra="allow")
