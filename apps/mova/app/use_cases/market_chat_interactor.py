"""채팅 Interactor — ChatUseCase 구현체."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from mova.adapter.inbound.api.schemas.market_chat_schema import MovaChatRequest
from mova.adapter.outbound.llm.chat_prompt import ChatPromptBuilder
from mova.adapter.outbound.llm.chat_reply import ChatReplyService
from mova.adapter.outbound.llm.gemini_client import gemini_reply
from mova.adapter.outbound.llm.intent_extraction import IntentExtractionService
from mova.app.dtos.market_chat_dto import ChatRecommendationDto, ChatResponseDto
from mova.app.ports.input.market_chat_use_case import ChatUseCase
from mova.app.ports.output.market_chat_repository import ChatRepositoryPort

logger = logging.getLogger(__name__)


class ChatInteractor(ChatUseCase):
    def __init__(self, repository: ChatRepositoryPort) -> None:
        self._repo = repository
        self._intent_svc = IntentExtractionService()
        self._prompt_builder = ChatPromptBuilder()
        self._reply_svc = ChatReplyService()

    async def chat(self, request: MovaChatRequest) -> ChatResponseDto:
        # 1. 의도 추출 (Gemini flash or fallback)
        intent = await asyncio.to_thread(self._intent_svc.extract, request.message)

        # 2. 태그 카탈로그 검색 + 사용자 컨텍스트 (병렬)
        catalog_task = self._repo.search_tag_catalog(intent["keywords"][:6], limit=12)
        if request.user_id:
            intents_task = self._repo.get_recent_intents_by_user(request.user_id, limit=3)
            prefs_task = self._repo.get_user_preferences(request.user_id)
            catalog, past_intents, (nickname, preferred_genres) = await asyncio.gather(
                catalog_task, intents_task, prefs_task
            )
        else:
            catalog = await catalog_task
            past_intents, nickname, preferred_genres = [], None, []

        # 3. 프롬프트 빌드 → Gemini 추천
        prompt = self._prompt_builder.build_prompt(
            request.history_dicts(),
            request.message,
            refined_query=intent["refined_query"],
            keywords=intent["keywords"],
            intent_type=intent["intent_type"],
            search_filters=intent["search_filters"],
            past_intents=past_intents,
            tag_catalog=catalog,
            user_nickname=nickname,
            preferred_genres=preferred_genres,
        )
        raw = await asyncio.to_thread(gemini_reply, prompt, request.model)
        reply, recs = self._reply_svc.parse_gemini_reply(raw)
        recs = await self._reply_svc.enrich_from_db(recs)

        # 4. chat + picks 저장
        batch_at = datetime.now(timezone.utc)
        chat_id = await self._repo.save_chat(
            user_id=request.user_id,
            assistant_id=None,
            raw_message=request.message,
            refined_query=intent["refined_query"],
            keywords=intent["keywords"],
            intent_type=intent["intent_type"],
            search_filters=intent["search_filters"],
        )
        await self._repo.save_picks(
            chat_id=chat_id,
            user_id=request.user_id,
            recommendations=recs,
            batch_at=batch_at,
        )

        logger.info(
            "[ChatInteractor] chat_id=%d intent=%s recs=%d",
            chat_id, intent["intent_type"], len(recs),
        )
        return ChatResponseDto(
            chat_id=chat_id,
            reply=reply,
            refined_query=intent["refined_query"],
            keywords=intent["keywords"],
            intent_type=intent["intent_type"],
            search_filters=intent["search_filters"],
            recommendations=[
                ChatRecommendationDto(
                    id=r.id,
                    title=r.title,
                    year=r.year,
                    poster=r.poster,
                    synopsis=r.synopsis,
                    platform=r.platform,
                    hook=r.hook,
                )
                for r in recs
            ],
        )
