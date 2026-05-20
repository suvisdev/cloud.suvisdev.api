import json
import logging
import re

from mova.app.models.movies_model import slugify_movie
from mova.app.repositories.movies_repository import MoviesRepository
from mova.app.schemas.audience_schema import MovaChatRecommendationSchema

logger = logging.getLogger(__name__)


def _coerce_poster(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        for key in ("url", "src", "href", "poster"):
            nested = value.get(key)
            if isinstance(nested, str) and nested.strip():
                return nested.strip()
        return ""
    return str(value).strip() if value else ""


class MovaChatReplyService:
    def parse_gemini_reply(self, raw: str) -> tuple[str, list[MovaChatRecommendationSchema]]:
        data = self._extract_json(raw)
        intro = str(data.get("intro", "")).strip() if data else raw.strip()[:300]
        picks = data.get("picks") if data else None

        recommendations: list[MovaChatRecommendationSchema] = []

        if isinstance(picks, list):
            for item in picks[:3]:
                if not isinstance(item, dict):
                    continue
                title = str(item.get("title", "")).strip()
                if not title:
                    title = str(item.get("slug", "")).strip()
                if not title:
                    continue
                hook = str(item.get("hook", "")).strip()[:120]
                platform_raw = item.get("platform")
                platform = (
                    str(platform_raw).strip()
                    if isinstance(platform_raw, str) and platform_raw.strip()
                    else None
                )
                recommendations.append(
                    MovaChatRecommendationSchema(
                        id=slugify_movie(title),
                        title=title,
                        year=str(item.get("year", "")).strip() or "",
                        poster=_coerce_poster(item.get("poster")),
                        synopsis=str(item.get("synopsis", "")).strip()[:100] or "",
                        platform=platform,
                        hook=hook or "취향에 맞는 작품이에요.",
                    ),
                )

        if not intro and recommendations:
            intro = "요청하신 취향에 맞춰 아래 작품 3편을 골라봤어요."
        elif not intro:
            intro = "추천을 준비하지 못했어요. 다시 질문해 주세요."

        return intro, recommendations[:3]

    async def enrich_from_db(
        self,
        recommendations: list[MovaChatRecommendationSchema],
    ) -> list[MovaChatRecommendationSchema]:
        """DB에 저장된 영화 메타(포스터·slug·연도)로 추천 카드를 보강한다."""
        if not recommendations:
            return []
        repo = MoviesRepository()
        enriched: list[MovaChatRecommendationSchema] = []
        for rec in recommendations:
            movie = await repo.get_by_slug(rec.id) or await repo.find_by_title(rec.title)
            poster = _coerce_poster(rec.poster)
            year = rec.year
            platform = rec.platform
            slug = rec.id
            if movie is not None:
                slug = movie.slug
                if not poster:
                    poster = (movie.poster_url or "").strip()
                if not year:
                    year = movie.release_year or ""
                if not platform and movie.platform:
                    platform = movie.platform
            enriched.append(
                rec.model_copy(
                    update={
                        "id": slug,
                        "poster": poster,
                        "year": year,
                        "platform": platform,
                    },
                ),
            )
        return enriched

    def _extract_json(self, raw: str) -> dict | None:
        text = raw.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{[\s\S]*\}", text)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
        logger.warning("[MovaChatReplyService] JSON 파싱 실패")
        return None
