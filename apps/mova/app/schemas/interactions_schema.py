from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

InteractionActionType = Literal["favorite", "watched", "click", "not_interested"]


class InteractionCreateSchema(BaseModel):
    user_id: int = Field(..., gt=0)
    movie_id: int = Field(..., gt=0)
    action_type: InteractionActionType = Field(
        ...,
        description="favorite=찜하기, watched=봤어요, click=클릭, not_interested=관심 없음",
    )


class InteractionSchema(BaseModel):
    id: int
    user_id: int
    movie_id: int
    action_type: str
    action_at: datetime


class InteractionWithMovieSchema(BaseModel):
    id: int
    user_id: int
    movie_id: int
    action_type: str
    action_at: datetime
    movie_title: str
    movie_slug: str
