from __future__ import annotations

import logging
from datetime import date

from mova.app.dtos.studio_import_dto import (
    MovieImportResultDto,
    MovieUpsertCommand,
    StudioImportQuery,
    StudioImportResponse,
    TmdbImportCommand,
    TmdbMovieSnapshotDto,
)
from mova.app.ports.input.import_use_case import ImportUseCase
from mova.app.ports.output.market_rankings_repository import RankingsRepositoryPort
from mova.app.ports.output.movies_repository import MoviesRepositoryPort
from mova.app.ports.output.tmdb_catalog_port import TmdbCatalogPort

logger = logging.getLogger(__name__)

MIN_CATALOG_MOVIES = 5
SEED_POPULAR_PAGES = 2
SEED_RANKING_LIMIT = 10
SEARCH_IMPORT_LIMIT = 5


class ImportInteractor(ImportUseCase):
    def __init__(
        self,
        movies: MoviesRepositoryPort,
        catalog: TmdbCatalogPort,
        rankings: RankingsRepositoryPort,
    ) -> None:
        self._movies = movies
        self._catalog = catalog
        self._rankings = rankings

    async def introduce_myself(self, query: StudioImportQuery) -> StudioImportResponse:
        return StudioImportResponse(id=query.id, name=query.name)

    async def seed_catalog_if_sparse(self) -> MovieImportResultDto:
        count = await self._movies.count_movies()
        if count >= MIN_CATALOG_MOVIES:
            return MovieImportResultDto(
                imported=0,
                message=f"카탈로그 {count}편 — 시드 생략 (기준 {MIN_CATALOG_MOVIES}편)",
            )
        snapshots: list[TmdbMovieSnapshotDto] = []
        for page in range(1, SEED_POPULAR_PAGES + 1):
            snapshots.extend(await self._catalog.fetch_popular(page=page))
        return await self._persist_snapshots(snapshots, update_rankings=True)

    async def import_tmdb(self, command: TmdbImportCommand) -> MovieImportResultDto:
        snapshots = await self._resolve_snapshots(command)
        return await self._persist_snapshots(snapshots, update_rankings=False)

    async def _persist_snapshots(
        self,
        snapshots: list[TmdbMovieSnapshotDto],
        *,
        update_rankings: bool,
    ) -> MovieImportResultDto:
        if not snapshots:
            return MovieImportResultDto(imported=0, message="가져올 TMDB 작품이 없습니다.")

        pairs: list[tuple[int, TmdbMovieSnapshotDto]] = []
        for snap in snapshots:
            movie_id = await self._movies.upsert_movie(self._to_upsert(snap))
            pairs.append((movie_id, snap))

        rankings_updated = False
        if update_rankings and pairs:
            ranked_ids = [
                movie_id
                for movie_id, _ in sorted(pairs, key=lambda pair: pair[1].rating, reverse=True)[
                    :SEED_RANKING_LIMIT
                ]
            ]
            saved = await self._rankings.save_box_office_ranking(ranked_ids, date.today())
            rankings_updated = saved > 0

        movie_ids = [movie_id for movie_id, _ in pairs]
        logger.info(
            "[ImportInteractor] persisted=%d rankings=%s",
            len(movie_ids),
            rankings_updated,
        )
        return MovieImportResultDto(
            imported=len(movie_ids),
            movie_ids=movie_ids,
            rankings_updated=rankings_updated,
            message=f"TMDB에서 {len(movie_ids)}편 반영",
        )

    async def _resolve_snapshots(self, command: TmdbImportCommand) -> list[TmdbMovieSnapshotDto]:
        if command.tmdb_id is not None:
            return [await self._catalog.fetch_by_id(command.tmdb_id)]

        if command.query and command.query.strip():
            found = await self._catalog.search(command.query.strip(), page=1)
            return found[:SEARCH_IMPORT_LIMIT]

        pages = max(0, command.popular_pages)
        if pages > 0:
            snapshots: list[TmdbMovieSnapshotDto] = []
            for page in range(1, pages + 1):
                snapshots.extend(await self._catalog.fetch_popular(page=page))
            return snapshots

        return []

    @staticmethod
    def _to_upsert(snap: TmdbMovieSnapshotDto) -> MovieUpsertCommand:
        return MovieUpsertCommand(
            slug=snap.slug,
            title=snap.title,
            release_year=snap.release_year,
            rating=snap.rating,
            poster_url=snap.poster_url,
            genres=snap.genres,
        )
