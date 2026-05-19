from pydantic import BaseModel, Field


class MovaSearchItemSchema(BaseModel):
    id: str
    title: str
    year: str
    rating: float
    poster: str
    match_type: str = Field(description="title | person | keyword | synopsis")


class MovaCastSchema(BaseModel):
    name: str
    role: str
    photo: str


class MovaCommentSchema(BaseModel):
    id: str
    user: str
    rating: float
    text: str
    likes: int
    commentCount: int


class MovaTitleDetailSchema(BaseModel):
    id: str
    title: str
    year: str
    genres: list[str]
    country: str
    ageRating: str
    rankBadge: str | None = None
    platform: str | None = None
    poster: str
    backdrop: str
    rating: float
    ratingCount: int
    rank: int
    badge: str | None = None
    synopsis: str
    ratingDistribution: list[int]
    cast: list[MovaCastSchema]
    comments: list[MovaCommentSchema]
    gallery: list[str]
