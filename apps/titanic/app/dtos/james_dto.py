from __future__ import annotations

from pydantic import BaseModel, Field


class JamesRowPayload(BaseModel):
    passenger_id: str = ""
    survived: str = ""
    pclass: str = ""
    name: str = ""
    gender: str = ""
    age: str = ""
    sibsp: str = ""
    parch: str = ""
    ticket: str = ""
    fare: str = ""
    cabin: str = ""
    embarked: str = ""


class JamesUploadResult(BaseModel):
    row_count: int = 0
    rows: list[JamesRowPayload] = Field(default_factory=list)
