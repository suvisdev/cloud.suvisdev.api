from __future__ import annotations

import logging
from typing import Literal

from mova.adapter.inbound.api.gemini_reply import gemini_reply
from mova.adapter.inbound.api.schemas.chat_schema import MovaChatResponseSchema
from mova.adapter.inbound.api.schemas.movies_schema import MovieTitleCreateSchema
from mova.adapter.outbound.llm.chat_prompt import ChatPromptBuilder
from mova.adapter.outbound.llm.intent_extraction import (
    MAX_CHAT_KEYWORDS,
    IntentExtractionService,
    merge_keyword_lists,
)
from mova.adapter.outbound.pg.assistants_pg_repository import AssistantsPgRepository
from mova.adapter.outbound.pg.chat_pg_repository import ChatPgRepository
from mova.adapter.outbound.pg.movies_pg_repository import MoviesPgRepository
from mova.adapter.outbound.pg.picks_pg_repository import PicksPgRepository
from mova.app.ports.input.chat_use_case import ChatUseCase
from mova.app.ports.output.assistants_repository import AssistantsRepository
from mova.app.ports.output.chat_repository import ChatRepository
from mova.app.ports.output.movies_repository import MoviesRepository
from mova.app.ports.output.picks_repository import PicksRepository
from mova.app.use_cases.movies_interactor import MoviesInteractor
from mova.app.use_cases.search_interactor import SearchInteractor
from friday13th.app.dtos.member_model import MemberRepository
from friday13th.app.dtos.user_model import get_secom_user_profile

logger = logging.getLogger(__name__)


class ChatInteractor(ChatUseCase):
    def __init__(self) -> None:
        self.chat_prompt = ChatPromptBuilder()
        self.intent_extraction_service = IntentExtractionService()
        self.chat_repository: ChatRepository = ChatPgRepository()
        self.movies_interactor = MoviesInteractor()
        self.picks_repository: PicksRepository = PicksPgRepository()
        self.movies_repository: MoviesRepository = MoviesPgRepository()
        self.search_interactor = SearchInteractor()

    async def prepare_chat_context(
        self,
        message: str,
        *,
        user_id: int | None = None,
    ) -> dict:
        logger.info("[ChatInteractor] prepare_chat_context 진입")

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
        member_id: int | None = None
        assistant_id: int | None = None
        if user_id is not None:
            try:
                member = await MemberRepository().ensure_for_user(user_id)
                member_id = member.id
            except Exception:
                logger.exception("[ChatInteractor] member ensure 실패 user_id=%s", user_id)
        try:
            assistant_repo: AssistantsRepository = AssistantsPgRepository()
            assistant = await assistant_repo.get_default()
            if assistant is not None:
                assistant_id = assistant.id
        except Exception:
            logger.exception("[ChatInteractor] default assistant 조회 실패")

        try:
            chat_id = await self.chat_repository.upsert(
                raw_message=message,
                refined_query=refined,
                keywords=keywords,
                intent_type=intent_type,
                search_filters=search_filters,
                user_id=user_id,
                member_id=member_id,
                assistant_id=assistant_id,
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
                "[ChatInteractor] DB 미연결 — 의도 저장·태그 검색·과거 취향 생략",
                exc_info=True,
            )

        mova_user = None
        if user_id is not None:
            try:
                mova_user = await get_secom_user_profile(user_id)
            except Exception:
                logger.warning(
                    "[ChatInteractor] user_id=%s Secom 프로필 로드 실패",
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

    async def _save_picks(self, context: dict, recommendations: list) -> None:
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
                    "[ChatInteractor] picks skip — title=%r slug=%r",
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
            logger.exception("[ChatInteractor] picks 저장 실패")

    async def _search_movies_by_intent(
        self,
        refined_query: str,
        keywords: list[str],
        *,
        intent_type: str = "mood",
        search_filters: dict | None = None,
    ) -> list:
        try:
            hits = await self.search_interactor.search_by_intent(
                refined_query=refined_query,
                keywords=keywords,
                intent_type=intent_type,
                search_filters=search_filters or {},
                limit=12,
            )
            logger.info(
                "[ChatInteractor] tag_catalog — intent=%s hits=%s",
                intent_type,
                len(hits),
            )
            return hits
        except Exception:
            logger.warning("[ChatInteractor] intent search failed", exc_info=True)
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
        return self.chat_prompt.build_prompt(
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
        intro, recommendations = self.chat_prompt.parse_structured_reply(raw_gemini)

        if recommendations:
            try:
                titles = [r.title for r in recommendations]
                for title in titles:
                    await self.movies_interactor.save_title(MovieTitleCreateSchema(title=title))
            except Exception:
                logger.exception("[ChatInteractor] 추천 영화 제목 DB 저장 실패")
            try:
                recommendations = await self.chat_prompt.reply_service.enrich_from_db(
                    recommendations,
                )
            except Exception:
                logger.exception("[ChatInteractor] 추천 영화 DB 메타 보강 실패")

            await self._save_picks(context, recommendations)

        return MovaChatResponseSchema(
            reply=intro,
            recommendations=recommendations,
            refined_query=context.get("refined_query") or None,
            keywords=context.get("keywords") or [],
            intent_type=context.get("intent_type"),
            search_filters=context.get("search_filters") or {},
        )

    async def chat(
        self,
        message: str,
        history: list[dict[str, str]],
        *,
        user_id: int | None = None,
        model_key: Literal["flash", "flash15", "pro"] | None = None,
    ) -> MovaChatResponseSchema:
        context = await self.prepare_chat_context(message, user_id=user_id)
        prompt = await self.build_prompt(history, message, context=context)
        raw = gemini_reply(prompt, model_key)
        return await self.build_response(raw, context)
