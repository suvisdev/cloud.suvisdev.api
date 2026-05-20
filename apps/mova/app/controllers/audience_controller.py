import logging

from mova.app.repositories.audience_repository import ChatIntentRepository
from mova.app.schemas.audience_schema import MovaChatResponseSchema
from mova.app.services.audience_service import MovaChatService
from mova.app.services.intent_extraction_service import IntentExtractionService
from mova.app.services.movies_service import MoviesService
from mova.app.services.users_service import UsersService

logger = logging.getLogger(__name__)


class MovaChatController:
    def __init__(self) -> None:
        self.mova_chat_service = MovaChatService()
        self.intent_extraction_service = IntentExtractionService()
        self.chat_intent_repository = ChatIntentRepository()
        self.movies_service = MoviesService()
        self.users_service = UsersService()

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
        try:
            await self.chat_intent_repository.upsert(
                raw_message=message,
                refined_query=refined,
                keywords=keywords,
            )
            past_all = await self.chat_intent_repository.get_top_for_context(limit=8)
            past_intents = [
                p
                for p in past_all
                if p.refined_query.strip().lower() != refined.lower()
            ][:6]
        except Exception:
            logger.warning(
                "[MovaChatController] DB 미연결 — 의도 저장·과거 취향 조회 생략, Gemini 추천만 진행",
                exc_info=True,
            )

        mova_user = None
        if user_id is not None:
            try:
                mova_user = await self.users_service.get_user(user_id)
            except Exception:
                logger.warning(
                    "[MovaChatController] user_id=%s 프로필 로드 실패 — 취향 미반영",
                    user_id,
                )

        return {
            "refined_query": refined,
            "keywords": keywords,
            "past_intents": past_intents,
            "mova_user": mova_user,
        }

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
            user_nickname=user.nickname if user else None,
            preferred_genres=user.preferred_genres if user else None,
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
