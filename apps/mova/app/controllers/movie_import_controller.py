import logging

from mova.app.schemas.movie_import_schema import MovieImportResultSchema
from mova.app.services.movie_import_service import MovieImportService

logger = logging.getLogger(__name__)


class MovieImportController:
    def __init__(self) -> None:
        self.service = MovieImportService()

    async def import_popular(
        self,
        *,
        pages: int = 2,
        setup_rankings: bool = True,
    ) -> MovieImportResultSchema:
        logger.info("[MovieImportController] import_popular — pages=%s", pages)
        return await self.service.import_popular(
            pages=pages,
            setup_rankings=setup_rankings,
        )

    async def import_search(
        self,
        query: str,
        *,
        pages: int = 1,
        setup_rankings: bool = False,
    ) -> MovieImportResultSchema:
        logger.info("[MovieImportController] import_search — q=%r", query.strip())
        return await self.service.import_search(query, pages=pages, setup_rankings=setup_rankings)

    async def import_by_tmdb_id(self, tmdb_id: int) -> MovieImportResultSchema:
        logger.info("[MovieImportController] import_by_tmdb_id — %s", tmdb_id)
        return await self.service.import_movie_by_tmdb_id(tmdb_id)

    async def import_by_kofic_cd(self, movie_cd: str) -> MovieImportResultSchema:
        logger.info("[MovieImportController] import_by_kofic_cd — %s", movie_cd)
        return await self.service.import_movie_by_kofic_cd(movie_cd)

    async def import_kofic_daily(
        self,
        *,
        target_date: str,
        setup_rankings: bool = True,
    ) -> MovieImportResultSchema:
        logger.info("[MovieImportController] import_kofic_daily — %s", target_date)
        return await self.service.import_kofic_daily(
            target_date=target_date,
            setup_rankings=setup_rankings,
        )

    async def import_kofic_weekly(
        self,
        *,
        target_date: str,
        week_gb: str = "0",
        setup_rankings: bool = True,
    ) -> MovieImportResultSchema:
        logger.info(
            "[MovieImportController] import_kofic_weekly — %s (week_gb=%s)",
            target_date,
            week_gb,
        )
        return await self.service.import_kofic_weekly(
            target_date=target_date,
            week_gb=week_gb,
            setup_rankings=setup_rankings,
        )

    async def enrich_missing_posters(self, *, limit: int = 50) -> MovieImportResultSchema:
        logger.info("[MovieImportController] enrich_missing_posters — limit=%s", limit)
        return await self.service.enrich_missing_posters(limit=limit)
