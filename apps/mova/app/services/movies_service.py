import logging

from mova.app.data.movie_catalog import resolve_canonical_slug, title_for_canonical_slug
from mova.app.repositories.movies_repository import MoviesRepository, MoviesRepositoryError
from mova.app.schemas.mova_title_schema import MovaTitleCastSchema, MovaTitleDetailSchema
from mova.app.schemas.movies_schema import (
    MovieCreateSchema,
    MovieSchema,
    MovieTitleCreateSchema,
    MovieTitleSchema,
)
from mova.app.services.characters_service import CharactersService
from mova.app.services.reviews_service import ReviewsService

logger = logging.getLogger(__name__)


class MoviesService:
    def __init__(self) -> None:
        self.movies_repository = MoviesRepository()

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
        logger.info("[MoviesService] save_movie — %r", payload.title)
        row = await self.movies_repository.upsert(self._create_to_dict(payload))
        return self._to_schema(row)

    async def save_title(self, payload: MovieTitleCreateSchema) -> MovieTitleSchema:
        title = payload.title.strip()
        logger.info("[MoviesService] save_title — %r", title)
        movie_id = await self.movies_repository.upsert_title(title)
        return MovieTitleSchema(id=movie_id, title=title)

    async def save_titles(self, titles: list[str]) -> list[MovieTitleSchema]:
        cleaned = [t.strip() for t in titles if t and str(t).strip()]
        if not cleaned:
            return []

        seen: set[str] = set()
        unique: list[str] = []
        for t in cleaned:
            if t not in seen:
                seen.add(t)
                unique.append(t)

        logger.info("[MoviesService] save_titles — count=%s", len(unique))
        ids = await self.movies_repository.upsert_titles(unique)
        return [MovieTitleSchema(id=movie_id, title=title) for movie_id, title in zip(ids, unique)]

    async def list_movies(self, limit: int = 100) -> list[MovieSchema]:
        rows = await self.movies_repository.list_movies(limit=limit)
        return [self._to_schema(r) for r in rows]

    async def list_titles(self, limit: int = 100) -> list[MovieTitleSchema]:
        rows = await self.movies_repository.list_titles(limit=limit)
        return [MovieTitleSchema(id=row.id, title=row.title) for row in rows]

    async def get_movie(self, movie_id: int) -> MovieSchema:
        row = await self.movies_repository.get_by_id(movie_id)
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
            row = await self.movies_repository.get_by_slug(key)
        canonical = resolve_canonical_slug(key)
        if row is None:
            row = await self.movies_repository.get_by_slug(canonical)
        if row is None and canonical != key:
            row = await self.movies_repository.get_by_slug(key)
        if row is None:
            row = await self.movies_repository.find_by_title(key)
        if row is None:
            catalog_title = title_for_canonical_slug(canonical)
            if catalog_title:
                row = await self.movies_repository.find_by_title(catalog_title)
        if row is None:
            raise MoviesRepositoryError(
                f"영화 slug '{slug}'를 찾을 수 없습니다.",
                status_code=404,
            )

        cast_rows = await CharactersService().list_actors_by_movie(row.id, limit=50)
        cast = [
            MovaTitleCastSchema(
                name=a.actor_name,
                role="감독" if a.role_type == "director" else "출연",
                photo=a.profile_photo or "",
            )
            for a in cast_rows
        ]

        rating_count = 0
        rating = float(row.rating or 0)
        try:
            summary = await ReviewsService().get_movie_rating_summary(row.id)
            rating_count = summary.review_count
            rating = float(summary.average_rating)
        except Exception:
            logger.debug("[MoviesService] rating summary skipped for movie_id=%s", row.id)

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
