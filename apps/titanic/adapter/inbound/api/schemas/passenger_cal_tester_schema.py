from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PassengerCalTesterSchema(BaseModel):
    """passenger_cal_tester schema (extend later)."""

    model_config = ConfigDict(extra="allow")
