from __future__ import annotations

from pydantic import BaseModel, Field


class WalterSchema(BaseModel):
    id: int = 1
    name: str = Field(default="Walter")
    memo: str = Field(default="월터는 타이타닉의 승무원이다")
