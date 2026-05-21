import logging

from mova.app.repositories.chat_repository import ChatRepository
from mova.app.schemas.audience_schema import MovaChatResponseSchema
from mova.app.services.audience_service import MovaChatService
from mova.app.services.intent_extraction_service import IntentExtractionService
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

    async def prepare_chat_context(
        self,
        message: str,
        *,
        user_id: int | None = None,
    ) -> dict:
        logger.info("[MovaChatController] prepare_chat_context 진입")

        extracted = self.intent_extraction_service.extract(message)
        refined = str(extracted.get("refined_query", "")).strip()
        keywords = extracted.get("keywords") or []
        if isinstance(keywords, list):
            keywords = [str(k).strip() for k in keywords if str(k).strip()]
        else:
            keywords = []

        if not refined:
            refined = message.strip()[:255]

        past_intents: list = []
        tag_catalog: list = []
        try:
            await self.chat_repository.upsert(
                raw_message=message,
                refined_query=refined,
                keywords=keywords,
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
            tag_catalog = await self._search_movies_by_intent(refined, keywords)
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
            "past_intents": past_intents,
            "tag_catalog": tag_catalog,
            "mova_user": mova_user,
        }

    async def _search_movies_by_intent(
        self,
        refined_query: str,
        keywords: list[str],
    ) -> list:
        """chat 의도 → GET /mova/search 와 동일: tags.label 등으로 movies 조회."""
        search = SearchService()
        seen: set[str] = set()
        hits = []
        queries: list[str] = []
        if refined_query.strip():
            queries.append(refined_query.strip())
        for kw in keywords:
            if kw.strip() and kw.strip() not in queries:
                queries.append(kw.strip())
        for q in queries[:5]:
            try:
                batch = await search.search(q, limit=8)
            except Exception:
                logger.warning("[MovaChatController] intent search failed — q=%r", q, exc_info=True)
                continue
            for item in batch:
                if item.id in seen:
                    continue
                seen.add(item.id)
                hits.append(item)
                if len(hits) >= 12:
                    return hits
        logger.info(
            "[MovaChatController] tag_catalog — queries=%s hits=%s",
            queries,
            len(hits),
        )
        return hits

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

        return MovaChatResponseSchema(
            reply=intro,
            recommendations=recommendations,
            refined_query=context.get("refined_query") or None,
            keywords=context.get("keywords") or [],
        )
