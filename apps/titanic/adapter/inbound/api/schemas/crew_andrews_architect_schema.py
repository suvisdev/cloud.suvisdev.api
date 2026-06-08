from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CrewAndrewsArchitectSchema(BaseModel):
    """crew_andrews_architect schema (extend later)."""

    model_config = ConfigDict(extra="allow")
