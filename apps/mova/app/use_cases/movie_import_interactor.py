from __future__ import annotations

from datetime import date

from core.matrix.keymaker_api import get_keymaker
from mova.adapter.inbound.api.schemas.movie_import_schema import MovieImportResultSchema
from mova.adapter.inbound.api.schemas.rankings_schema import RankingBulkSchema, RankingItemCreateSchema
from mova.domain.value_objects.ranking_source import RANKING_SOURCE_BOX_OFFICE
from mova.adapter.outbound.http import (
    KoficAdapter,
    KoficAdapterError,
    TmdbAdapter,
    TmdbAdapterError,
)
from mova.app.ports.input.movie_import_use_case import MovieImportUseCase
from mova.app.ports.input.rankings_use_case import RankingsUseCase
from mova.app.ports.output.movies_repository import MoviesRepository

_TMDB_SLUG_PREFIX = "tmdb-"
_KOFIC_SLUG_PREFIX = "kofic-"


def tmdb_slug(tmdb_id: int) -> str:
    return f"{_TMDB_SLUG_PREFIX}{int(tmdb_id)}"


def kofic_slug(movie_cd: str) -> str:
    return f"{_KOFIC_SLUG_PREFIX}{str(movie_cd).strip()}"


def _clamp(value: int, lo: int, hi: int) -> int:
    return min(max(value, lo), hi)


def _resolve_kofic_target_date(target_date: str | None) -> str:
    raw = (target_date or KoficAdapter.default_target_date()).strip()
    if len(raw) != 8 or not raw.isdigit():
        raise KoficAdapterError("target_date 형식은 YYYYMMDD 입니다.", status_code=400)
    return raw


def _validate_week_gb(week_gb: str) -> str:
    if week_gb not in ("0", "1"):
        raise KoficAdapterError("week_gb는 0(주간) 또는 1(주말)만 가능합니다.", status_code=400)
    return week_gb


class MovieImportInteractor(MovieImportUseCase):
    def __init__(
        self,
        movies_repository: MoviesRepository | None = None,
        rankings_use_case: RankingsUseCase | None = None,
    ) -> None:
        # LLM adapter는 enrichment 용으로만 이 interactor를 호출하는 경우가 많아서,
        # 기본값 주입으로 adapter/outbound 계층 간 결합을 줄입니다.
        if movies_repository is None:
            from mova.adapter.outbound.pg.movies_pg_repository import MoviesPgRepository

            movies_repository = MoviesPgRepository()
        if rankings_use_case is None:
            from mova.adapter.outbound.pg.rankings_pg_repository import RankingsPgRepository
            from mova.app.use_cases.rankings_interactor import RankingsInteractor

            rankings_use_case = RankingsInteractor(RankingsPgRepository())

        self._movies_repository = movies_repository
        self._rankings_use_case = rankings_use_case

    def _adapter(self) -> TmdbAdapter:
        key = get_keymaker().tmdb_api_key
        return TmdbAdapter(key)

    def _kofic_adapter(self) -> KoficAdapter:
        key = get_keymaker().kofic_api_key
        return KoficAdapter(key)

    def _tmdb_adapter_optional(self) -> TmdbAdapter | None:
        key = get_keymaker().tmdb_api_key
        if not key:
            return None
        return TmdbAdapter(key)

    @staticmethod
    def _year_from_date(release_date: str | None) -> str:
        if not release_date or len(release_date) < 4:
            return ""
        return release_date[:4]

    def _movie_payload_from_tmdb(
        self,
        detail: dict,
        *,
        genre_map: dict[int, str] | None = None,
    ) -> dict:
        tmdb_id = int(detail["id"])
        genres: list[str] = []
        for g in detail.get("genres") or []:
            if g.get("name"):
                genres.append(str(g["name"]))
        if not genres and genre_map:
            for gid in detail.get("genre_ids") or []:
                name = genre_map.get(int(gid))
                if name:
                    genres.append(name)

        adapter = self._adapter()
        return {
            "slug": tmdb_slug(tmdb_id),
            "title": str(detail.get("title") or detail.get("original_title") or "").strip(),
            "release_year": self._year_from_date(detail.get("release_date")),
            "rating": round(float(detail.get("vote_average") or 0), 1),
            "poster": adapter.poster_url(detail.get("poster_path")),
            "genres": genres,
        }

    @staticmethod
    def _movie_payload_from_kofic(movie_info: dict, movie_cd: str) -> dict:
        title = str(movie_info.get("movieNm") or "").strip()
        open_dt = str(movie_info.get("openDt") or "").strip()
        release_year = open_dt[:4] if len(open_dt) >= 4 else ""
        genres = [
            str(g.get("genreNm")).strip()
            for g in (movie_info.get("genres") or [])
            if str(g.get("genreNm") or "").strip()
        ]
        return {
            "slug": kofic_slug(movie_cd),
            "title": title,
            "release_year": release_year,
            "rating": 0.0,
            "poster": "",
            "genres": genres,
        }

    async def enrich_payload_with_tmdb(self, payload: dict) -> dict:
        """KOFIC는 포스터 URL이 없어 TMDB 검색으로 poster·평점을 보강한다."""
        if str(payload.get("poster", "")).strip():
            return payload
        title = str(payload.get("title", "")).strip()
        if not title:
            return payload
        adapter = self._tmdb_adapter_optional()
        if adapter is None:
            return payload

        try:
            results = await adapter.search_movies(title, page=1)
            if not results:
                return payload

            target_year = str(payload.get("release_year", "")).strip()
            pick = results[0]
            for candidate in results:
                cand_title = str(candidate.get("title") or candidate.get("original_title") or "").strip()
                cand_year = self._year_from_date(candidate.get("release_date"))
                if cand_title == title and (not target_year or cand_year == target_year):
                    pick = candidate
                    break

            detail = await adapter.fetch_movie_detail(int(pick["id"]))
            poster = adapter.poster_url(detail.get("poster_path"))
            if poster:
                payload["poster"] = poster
            if float(payload.get("rating") or 0) <= 0:
                payload["rating"] = round(float(detail.get("vote_average") or 0), 1)
            if not payload.get("release_year"):
                payload["release_year"] = self._year_from_date(detail.get("release_date"))
            if not payload.get("genres"):
                payload["genres"] = [
                    str(g.get("name")).strip()
                    for g in (detail.get("genres") or [])
                    if str(g.get("name") or "").strip()
                ]
        except Exception:
            pass
        return payload

    async def _upsert_kofic_payload(self, payload: dict) -> int:
        enriched = await self.enrich_payload_with_tmdb(payload)
        row = await self._movies_repository.upsert(enriched)
        return row.id

    async def enrich_missing_posters(self, *, limit: int = 50) -> MovieImportResultSchema:
        """포스터가 비어 있는 영화(주로 KOFIC)에 TMDB 포스터를 채운다."""
        limit = _clamp(limit, 1, 100)
        rows = await self._movies_repository.list_movies(limit=max(limit * 3, 100))
        updated_ids: list[int] = []
        for row in rows:
            if row.poster_url:
                continue
            payload = {
                "slug": row.slug,
                "title": row.title,
                "release_year": row.release_year,
                "rating": row.rating,
                "poster": "",
                "genres": list(row.genres or []),
            }
            enriched = await self.enrich_payload_with_tmdb(payload)
            if not enriched.get("poster"):
                continue
            saved = await self._movies_repository.upsert(enriched)
            updated_ids.append(saved.id)
            if len(updated_ids) >= limit:
                break

        return MovieImportResultSchema(
            imported=len(updated_ids),
            movie_ids=updated_ids,
            message=f"TMDB 포스터 보강 {len(updated_ids)}편",
        )

    async def _upsert_tmdb_detail(self, detail: dict, *, genre_map: dict[int, str] | None) -> int:
        payload = self._movie_payload_from_tmdb(detail, genre_map=genre_map)
        if not payload["title"]:
            raise TmdbAdapterError("TMDB 영화 제목이 비어 있습니다.", status_code=400)
        row = await self._movies_repository.upsert(payload)
        return row.id

    async def import_movie_by_tmdb_id(self, tmdb_id: int) -> MovieImportResultSchema:
        adapter = self._adapter()
        detail = await adapter.fetch_movie_detail(tmdb_id)
        genre_map = await adapter.genre_map()
        movie_id = await self._upsert_tmdb_detail(detail, genre_map=genre_map)
        return MovieImportResultSchema(
            imported=1,
            movie_ids=[movie_id],
            message=f"TMDB {tmdb_id} 저장 완료",
        )

    async def import_movie_by_kofic_cd(self, movie_cd: str) -> MovieImportResultSchema:
        code = movie_cd.strip()
        if not code:
            raise KoficAdapterError("movie_cd가 비어 있습니다.", status_code=400)
        adapter = self._kofic_adapter()
        info = await adapter.fetch_movie_info(code)
        payload = self._movie_payload_from_kofic(info, code)
        if not payload["title"]:
            raise KoficAdapterError("KOFIC 영화 제목이 비어 있습니다.", status_code=400)
        movie_id = await self._upsert_kofic_payload(payload)
        return MovieImportResultSchema(
            imported=1,
            movie_ids=[movie_id],
            message=f"KOFIC {code} 저장 완료",
        )

    async def _import_summaries(
        self,
        summaries: list[dict],
        *,
        fetch_detail: bool,
    ) -> list[int]:
        if not summaries:
            return []
        adapter = self._adapter()
        genre_map = await adapter.genre_map()
        ids: list[int] = []
        seen: set[int] = set()

        for item in summaries:
            tmdb_id = item.get("id")
            if tmdb_id is None:
                continue
            tid = int(tmdb_id)
            if tid in seen:
                continue
            seen.add(tid)

            try:
                if fetch_detail:
                    detail = await adapter.fetch_movie_detail(tid)
                else:
                    detail = item
                movie_id = await self._upsert_tmdb_detail(detail, genre_map=genre_map)
                ids.append(movie_id)
            except Exception:
                pass

        return ids

    async def import_popular(
        self,
        *,
        pages: int = 2,
        setup_rankings: bool = True,
        ranking_limit: int = 10,
    ) -> MovieImportResultSchema:
        pages = _clamp(pages, 1, 5)
        adapter = self._adapter()
        summaries: list[dict] = []
        for page in range(1, max(1, pages) + 1):
            summaries.extend(await adapter.fetch_popular(page=page))

        movie_ids = await self._import_summaries(summaries, fetch_detail=True)
        rankings_updated = False
        if setup_rankings and movie_ids:
            rankings_updated = await self._setup_rankings_from_movie_ids(
                movie_ids[:ranking_limit],
            )

        return MovieImportResultSchema(
            imported=len(movie_ids),
            movie_ids=movie_ids,
            rankings_updated=rankings_updated,
            message=f"인기 영화 {len(movie_ids)}편 DB 반영",
        )

    async def import_search(
        self,
        query: str,
        *,
        pages: int = 1,
        setup_rankings: bool = False,
    ) -> MovieImportResultSchema:
        query = query.strip()
        if not query:
            raise TmdbAdapterError("검색어 q가 비어 있습니다.", status_code=400)
        pages = _clamp(pages, 1, 3)
        adapter = self._adapter()
        summaries: list[dict] = []
        for page in range(1, max(1, pages) + 1):
            summaries.extend(await adapter.search_movies(query, page=page))

        movie_ids = await self._import_summaries(summaries, fetch_detail=True)
        rankings_updated = False
        if setup_rankings and movie_ids:
            rankings_updated = await self._setup_rankings_from_movie_ids(movie_ids[:10])

        return MovieImportResultSchema(
            imported=len(movie_ids),
            movie_ids=movie_ids,
            rankings_updated=rankings_updated,
            message=f"검색 '{query.strip()}' — {len(movie_ids)}편 저장",
        )

    async def import_kofic_daily(
        self,
        *,
        target_date: str | None = None,
        setup_rankings: bool = True,
    ) -> MovieImportResultSchema:
        date_arg = _resolve_kofic_target_date(target_date)
        adapter = self._kofic_adapter()
        rows = await adapter.fetch_daily_boxoffice(date_arg)
        movie_ids: list[int] = []
        ranking_items: list[RankingItemCreateSchema] = []

        for item in rows[:10]:
            movie_cd = str(item.get("movieCd") or "").strip()
            if not movie_cd:
                continue
            info = await adapter.fetch_movie_info(movie_cd)
            payload = self._movie_payload_from_kofic(info, movie_cd)
            if not payload["title"]:
                continue
            movie_id = await self._upsert_kofic_payload(payload)
            movie_ids.append(movie_id)
            rank = int(item.get("rank") or len(ranking_items) + 1)
            rank_badge = str(item.get("rankOldAndNew") or "").strip().upper()
            ranking_items.append(
                RankingItemCreateSchema(
                    rank=rank,
                    movie_id=movie_id,
                    badge="NEW" if rank_badge == "NEW" else None,
                ),
            )

        rankings_updated = False
        if setup_rankings and ranking_items:
            await self._rankings_use_case.save_rankings(
                RankingBulkSchema(
                    ranked_at=date.today(),
                    source=RANKING_SOURCE_BOX_OFFICE,
                    items=ranking_items,
                ),
            )
            rankings_updated = True

        return MovieImportResultSchema(
            imported=len(movie_ids),
            movie_ids=movie_ids,
            rankings_updated=rankings_updated,
            message=f"KOFIC 일간 박스오피스 {len(movie_ids)}편 반영 ({date_arg})",
        )

    async def import_kofic_weekly(
        self,
        *,
        target_date: str | None = None,
        week_gb: str = "0",
        setup_rankings: bool = True,
    ) -> MovieImportResultSchema:
        date_arg = _resolve_kofic_target_date(target_date)
        week_gb = _validate_week_gb(week_gb)
        adapter = self._kofic_adapter()
        rows = await adapter.fetch_weekly_boxoffice(date_arg, week_gb=week_gb)
        movie_ids: list[int] = []
        ranking_items: list[RankingItemCreateSchema] = []

        for item in rows[:10]:
            movie_cd = str(item.get("movieCd") or "").strip()
            if not movie_cd:
                continue
            info = await adapter.fetch_movie_info(movie_cd)
            payload = self._movie_payload_from_kofic(info, movie_cd)
            if not payload["title"]:
                continue
            movie_id = await self._upsert_kofic_payload(payload)
            movie_ids.append(movie_id)
            rank = int(item.get("rank") or len(ranking_items) + 1)
            rank_badge = str(item.get("rankOldAndNew") or "").strip().upper()
            ranking_items.append(
                RankingItemCreateSchema(
                    rank=rank,
                    movie_id=movie_id,
                    badge="NEW" if rank_badge == "NEW" else None,
                ),
            )

        rankings_updated = False
        if setup_rankings and ranking_items:
            await self._rankings_use_case.save_rankings(
                RankingBulkSchema(
                    ranked_at=date.today(),
                    source=RANKING_SOURCE_BOX_OFFICE,
                    items=ranking_items,
                ),
            )
            rankings_updated = True

        return MovieImportResultSchema(
            imported=len(movie_ids),
            movie_ids=movie_ids,
            rankings_updated=rankings_updated,
            message=f"KOFIC 주간 박스오피스 {len(movie_ids)}편 반영 ({date_arg})",
        )

    async def _setup_rankings_from_movie_ids(self, movie_ids: list[int]) -> bool:
        if not movie_ids:
            return False
        rows: list[tuple] = []
        for mid in movie_ids:
            row = await self._movies_repository.get_by_id(mid)
            if row is not None:
                rows.append((row, float(row.rating or 0)))

        rows.sort(key=lambda x: x[1], reverse=True)
        items = [
            RankingItemCreateSchema(
                rank=idx,
                movie_id=row.id,
                badge="NEW" if idx <= 3 else None,
            )
            for idx, (row, _) in enumerate(rows[:10], start=1)
        ]
        if not items:
            return False
        await self._rankings_use_case.save_rankings(
            RankingBulkSchema(
                ranked_at=date.today(),
                source=RANKING_SOURCE_BOX_OFFICE,
                items=items,
            ),
        )
        return True

    async def seed_catalog_if_sparse(
        self,
        *,
        min_movies: int = 12,
        pages: int = 2,
    ) -> MovieImportResultSchema | None:
        """DB 영화가 적으면 TMDB 인기 목록으로 자동 채운다."""
        existing = await self._movies_repository.list_movies(limit=min_movies + 1)
        if len(existing) >= min_movies:
            return None
        key = get_keymaker().tmdb_api_key
        if not key:
            return None
        return await self.import_popular(pages=pages, setup_rankings=True)

    async def import_by_tmdb_id(self, tmdb_id: int) -> MovieImportResultSchema:
        return await self.import_movie_by_tmdb_id(tmdb_id)

    async def import_by_kofic_cd(self, movie_cd: str) -> MovieImportResultSchema:
        return await self.import_movie_by_kofic_cd(movie_cd)
