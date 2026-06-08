from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CrewSmithCaptainSchema(BaseModel):
    """crew_smith_captain schema (extend later)."""

    model_config = ConfigDict(extra="allow")
