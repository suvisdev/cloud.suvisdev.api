from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mova.adapter.inbound.api.schemas.movie_import_schema import MovieImportResultSchema


@dataclass
class MoviePayloadCommand:
    slug: str
    title: str
    release_year: str = ""
    rating: float = 0.0
    poster: str = ""
    genres: list[str] = field(default_factory=list)


@dataclass
class MovieImportResultDto:
    imported: int
    movie_ids: list[int] = field(default_factory=list)
    rankings_updated: bool = False
    message: str = ""

    def to_schema(self) -> MovieImportResultSchema:
        from mova.adapter.inbound.api.schemas.movie_import_schema import MovieImportResultSchema

        return MovieImportResultSchema(
            imported=self.imported,
            movie_ids=self.movie_ids,
            rankings_updated=self.rankings_updated,
            message=self.message,
        )
