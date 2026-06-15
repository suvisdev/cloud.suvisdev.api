from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ActorCreateSchema(BaseModel):
    name: str
    role_type: Literal["director", "actor"] = "actor"
    profile_photo: str = ""


class ActorSchema(BaseModel):
    id: int
    name: str
    role_type: str
    profile_photo: str


class StudioActorsSchema(BaseModel):

    id: int = Field(0, description="Actors ID")
    name: str = Field("배우 (Actor)", description="Actor's name")
    # 스크린을 채우는 실제 인물 데이터. actors 테이블 관리

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "배우 (Actor)",
            }
        }
    }
