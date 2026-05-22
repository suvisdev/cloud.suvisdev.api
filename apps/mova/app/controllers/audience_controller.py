import logging

from mova.app.repositories.chat_repository import ChatRepository
from mova.app.repositories.movies_repository import MoviesRepository
from mova.app.repositories.picks_repository import PicksRepository
from mova.app.schemas.audience_schema import MovaChatResponseSchema
from mova.app.services.audience_service import MovaChatService
from mova.app.services.intent_extraction_service import (
    MAX_CHAT_KEYWORDS,
    IntentExtractionService,
    merge_keyword_lists,
)
from mova.app.services.movies_service import MoviesService
from mova.app.services.search_service import SearchService
from secom.app.user_lookup import get_secom_user_profile

logger = logging.getLogger(__name__)


class MovaChatController:
    def __init__(self) -> None:
        self.mova_chat_service = MovaChatService()
        self.intent_extraction_service = IntentExtractionService()
        self.chat_repository = ChatRepository()
        self.movies_service = MoviesService()
        self.picks_repository = PicksRepository()
        self.movies_repository = MoviesRepository()

    async def prepare_chat_context(
        self,
        message: str,
        *,
        user_id: int | None = None,
    ) -> dict:
        logger.info("[MovaChatController] prepare_chat_context 진입")

        extracted = self.intent_extraction_service.extract(message)
        refined = str(extracted.get("refined_query", "")).strip()
        raw_kw = extracted.get("keywords") or []
        keywords = (
            merge_keyword_lists(raw_kw, limit=MAX_CHAT_KEYWORDS)
            if isinstance(raw_kw, list)
            else []
        )
        intent_type = str(extracted.get("intent_type") or "mood").strip() or "mood"
        search_filters = (
            extracted.get("search_filters")
            if isinstance(extracted.get("search_filters"), dict)
            else {}
        )

        if not refined:
            refined = message.strip()[:255]

        past_intents: list = []
        tag_catalog: list = []
        chat_id: int | None = None
        try:
            chat_id = await self.chat_repository.upsert(
                raw_message=message,
                refined_query=refined,
                keywords=keywords,
                intent_type=intent_type,
                search_filters=search_filters,
                user_id=user_id,
            )
            past_all = await self.chat_repository.get_top_for_context(
                limit=8,
                user_id=user_id,
            )
            past_intents = [
                p
                for p in past_all
                if p.refined_query.strip().lower() != refined.lower()
            ][:6]
            tag_catalog = await self._search_movies_by_intent(
                refined,
                keywords,
                intent_type=intent_type,
                search_filters=search_filters,
            )
        except Exception:
            logger.warning(
                "[MovaChatController] DB 미연결 — 의도 저장·태그 검색·과거 취향 생략, Gemini 추천만 진행",
                exc_info=True,
            )

        mova_user = None
        if user_id is not None:
            try:
                mova_user = await get_secom_user_profile(user_id)
            except Exception:
                logger.warning(
                    "[MovaChatController] user_id=%s Secom 프로필 로드 실패 — 취향 미반영",
                    user_id,
                )

        return {
            "refined_query": refined,
            "keywords": keywords,
            "intent_type": intent_type,
            "search_filters": search_filters,
            "past_intents": past_intents,
            "tag_catalog": tag_catalog,
            "mova_user": mova_user,
            "chat_id": chat_id,
            "user_id": user_id,
        }

    async def _save_picks(
        self,
        context: dict,
        recommendations: list,
    ) -> None:
        chat_id = context.get("chat_id")
        if chat_id is None or not recommendations:
            return
        rows: list[tuple[int, object, int]] = []
        for rank, rec in enumerate(recommendations, start=1):
            movie = await self.movies_repository.get_by_slug(rec.id) or await self.movies_repository.find_by_title(
                rec.title,
            )
            if movie is None:
                logger.warning(
                    "[MovaChatController] picks skip — movie not in DB title=%r slug=%r",
                    rec.title,
                    rec.id,
                )
                continue
            rows.append((movie.id, rec, rank))
        if not rows:
            return
        try:
            await self.picks_repository.save_chat_recommendations(
                chat_id=chat_id,
                user_id=context.get("user_id"),
                movie_ids=rows,
            )
        except Exception:
            logger.exception("[MovaChatController] picks 저장 실패")

    async def _search_movies_by_intent(
        self,
        refined_query: str,
        keywords: list[str],
        *,
        intent_type: str = "mood",
        search_filters: dict | None = None,
    ) -> list:
        """chat 의도·search_filters(AND) 기반 movies 후보."""
        search = SearchService()
        try:
            hits = await search.search_by_intent(
                refined_query=refined_query,
                keywords=keywords,
                intent_type=intent_type,
                search_filters=search_filters or {},
                limit=12,
            )
            logger.info(
                "[MovaChatController] tag_catalog — intent=%s filters=%s hits=%s",
                intent_type,
                search_filters,
                len(hits),
            )
            return hits
        except Exception:
            logger.warning(
                "[MovaChatController] intent search failed — intent=%s",
                intent_type,
                exc_info=True,
            )
            return []

    async def build_prompt(
        self,
        history: list[dict[str, str]],
        message: str,
        context: dict | None = None,
    ) -> str:
        if context is None:
            context = await self.prepare_chat_context(message)

        user = context.get("mova_user")
        return self.mova_chat_service.build_prompt(
            history,
            message,
            refined_query=context["refined_query"],
            keywords=context["keywords"],
            intent_type=context.get("intent_type") or "mood",
            search_filters=context.get("search_filters") or {},
            past_intents=context["past_intents"],
            tag_catalog=context.get("tag_catalog") or [],
            user_nickname=user.get("nickname") if user else None,
            preferred_genres=user.get("preferred_genres") if user else None,
        )

    async def build_response(
        self,
        raw_gemini: str,
        context: dict,
    ) -> MovaChatResponseSchema:
        intro, recommendations = self.mova_chat_service.parse_structured_reply(raw_gemini)

        if recommendations:
            try:
                await self.movies_service.save_titles([r.title for r in recommendations])
            except Exception:
                logger.exception("[MovaChatController] 추천 영화 제목 DB 저장 실패")
            try:
                recommendations = await self.mova_chat_service.reply_service.enrich_from_db(
                    recommendations,
                )
            except Exception:
                logger.exception("[MovaChatController] 추천 영화 DB 메타 보강 실패")

            await self._save_picks(context, recommendations)

        return MovaChatResponseSchema(
            reply=intro,
            recommendations=recommendations,
            refined_query=context.get("refined_query") or None,
            keywords=context.get("keywords") or [],
            intent_type=context.get("intent_type"),
            search_filters=context.get("search_filters") or {},
        )
