from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CrewHartleyViolinSchema(BaseModel):
    """crew_hartley_violin schema (extend later)."""

    model_config = ConfigDict(extra="allow")
