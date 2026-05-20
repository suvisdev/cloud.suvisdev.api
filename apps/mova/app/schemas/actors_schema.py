from typing import Literal

from pydantic import BaseModel, Field


class ActorCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    role_type: Literal["director", "actor"] = Field(default="actor", description="감독/배우")
    profile_photo: str = Field(default="", description="프로필 사진 URL/경로")


class ActorSchema(BaseModel):
    id: int
    name: str
    role_type: str
    profile_photo: str
