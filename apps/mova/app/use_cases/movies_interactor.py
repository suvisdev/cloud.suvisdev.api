from __future__ import annotations

from mova.adapter.inbound.api.schemas.search_schema import (
    MovaTitleCastSchema,
    MovaTitleDetailSchema,
)
from mova.adapter.inbound.api.schemas.movies_schema import (
    MovieCreateSchema,
    MovieSchema,
    MovieTitleCreateSchema,
    MovieTitleSchema,
)
from mova.adapter.outbound.pg.movies_pg_repository import MoviesRepositoryError
from mova.domain.value_objects.movie_catalog import (
    resolve_canonical_slug,
    title_for_canonical_slug,
)
from mova.app.ports.input.characters_use_case import CharactersUseCase
from mova.app.ports.input.movies_use_case import MoviesUseCase
from mova.app.ports.input.reviews_use_case import ReviewsUseCase
from mova.app.ports.output.movies_repository import MoviesRepository


class MoviesInteractor(MoviesUseCase):
    def __init__(
        self,
        repository: MoviesRepository,
        characters_use_case: CharactersUseCase,
        reviews_use_case: ReviewsUseCase,
    ) -> None:
        self._repository = repository
        self._characters_use_case = characters_use_case
        self._reviews_use_case = reviews_use_case

    def _to_schema(self, row) -> MovieSchema:
        return MovieSchema(
            id=row.id,
            slug=row.slug,
            title=row.title,
            release_year=row.release_year,
            rating=row.rating,
            poster=row.poster_url,
            platform=row.platform,
            genres=list(row.genres or []),
        )

    def _create_to_dict(self, payload: MovieCreateSchema) -> dict:
        return {
            "title": payload.title,
            "slug": payload.slug,
            "release_year": payload.release_year,
            "rating": payload.rating,
            "poster": payload.poster,
            "platform": payload.platform,
            "genres": payload.genres,
        }

    async def save_movie(self, payload: MovieCreateSchema) -> MovieSchema:
        row = await self._repository.upsert(self._create_to_dict(payload))
        return self._to_schema(row)

    async def save_title(self, payload: MovieTitleCreateSchema) -> MovieTitleSchema:
        title = payload.title.strip()
        movie_id = await self._repository.upsert_title(title)
        return MovieTitleSchema(id=movie_id, title=title)

    async def list_movies(self, limit: int = 100) -> list[MovieSchema]:
        rows = await self._repository.list_movies(limit=limit)
        return [self._to_schema(row) for row in rows]

    async def list_titles(self, limit: int = 100) -> list[MovieTitleSchema]:
        rows = await self._repository.list_titles(limit=limit)
        return [MovieTitleSchema(id=row.id, title=row.title) for row in rows]

    async def get_movie(self, movie_id: int) -> MovieSchema:
        row = await self._repository.get_by_id(movie_id)
        if row is None:
            raise MoviesRepositoryError(
                f"영화 ID {movie_id}를 찾을 수 없습니다.",
                status_code=404,
            )
        return self._to_schema(row)

    async def get_title_by_slug(self, slug: str) -> MovaTitleDetailSchema:
        key = slug.strip()
        row = None
        if key.startswith("tmdb-"):
            row = await self._repository.get_by_slug(key)
        canonical = resolve_canonical_slug(key)
        if row is None:
            row = await self._repository.get_by_slug(canonical)
        if row is None and canonical != key:
            row = await self._repository.get_by_slug(key)
        if row is None:
            row = await self._repository.find_by_title(key)
        if row is None:
            catalog_title = title_for_canonical_slug(canonical)
            if catalog_title:
                row = await self._repository.find_by_title(catalog_title)
        if row is None:
            raise MoviesRepositoryError(
                f"영화 slug '{slug}'를 찾을 수 없습니다.",
                status_code=404,
            )

        cast_rows = await self._characters_use_case.list_actors_by_movie(row.id, limit=50)
        cast = [
            MovaTitleCastSchema(
                name=actor.actor_name,
                role="감독" if actor.role_type == "director" else "출연",
                photo=actor.profile_photo or "",
            )
            for actor in cast_rows
        ]

        rating_count = 0
        rating = float(row.rating or 0)
        try:
            summary = await self._reviews_use_case.get_movie_rating_summary(row.id)
            rating_count = summary.review_count
            rating = float(summary.average_rating)
        except Exception:
            pass

        poster = row.poster_url or ""
        response_id = (
            row.slug
            if row.slug.startswith("tmdb-")
            else resolve_canonical_slug(row.slug, title=row.title)
        )
        return MovaTitleDetailSchema(
            id=response_id,
            title=row.title,
            year=row.release_year or "",
            genres=list(row.genres or []),
            platform=row.platform,
            poster=poster,
            backdrop=poster,
            rating=rating,
            ratingCount=rating_count,
            cast=cast,
        )
