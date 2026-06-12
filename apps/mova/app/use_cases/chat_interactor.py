from __future__ import annotations

from typing import Literal

from mova.adapter.outbound.llm.gemini_client import gemini_reply
from mova.adapter.inbound.api.schemas.chat_schema import MovaChatRequest
from mova.adapter.inbound.api.schemas.movies_schema import MovieTitleCreateSchema
from mova.adapter.outbound.llm.chat_prompt import ChatPromptBuilder
from mova.adapter.outbound.llm.intent_extraction import (
    MAX_CHAT_KEYWORDS,
    IntentExtractionService,
    merge_keyword_lists,
)
from mova.app.dtos.chat_dto import ChatMessageCommand, ChatResponseDto, ChatUpsertCommand
from mova.app.dtos.movies_dto import MovieTitleCommand
from mova.app.ports.input.chat_use_case import ChatUseCase
from mova.app.ports.input.movies_use_case import MoviesUseCase
from mova.app.ports.input.rankings_use_case import RankingsUseCase
from mova.app.ports.input.search_use_case import SearchUseCase
from mova.app.ports.output.assistants_repository import AssistantsRepository
from mova.app.ports.output.chat_repository import ChatRepository
from mova.app.ports.output.movies_repository import MoviesRepository
from mova.app.ports.output.picks_repository import PicksRepository
from viewer.adapter.outbound.orm.user_orm import get_viewer_user_profile


class ChatInteractor(ChatUseCase):
    def __init__(
        self,
        chat_repository: ChatRepository,
        picks_repository: PicksRepository,
        movies_repository: MoviesRepository,
        assistants_repository: AssistantsRepository,
        movies_use_case: MoviesUseCase,
        search_use_case: SearchUseCase,
        intent_extraction_service: IntentExtractionService,
        chat_prompt_builder: ChatPromptBuilder,
        rankings_use_case: RankingsUseCase,
    ) -> None:
        self._chat_repository = chat_repository
        self._picks_repository = picks_repository
        self._movies_repository = movies_repository
        self._assistants_repository = assistants_repository
        self._movies_use_case = movies_use_case
        self._search_use_case = search_use_case
        self._rankings_use_case = rankings_use_case
        self._intent_extraction_service = intent_extraction_service
        self._chat_prompt_builder = chat_prompt_builder

    async def prepare_chat_context(
        self,
        message: str,
        *,
        user_id: int | None = None,
    ) -> dict:
        extracted = self._intent_extraction_service.extract(message)
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
        assistant_id: int | None = None
        try:
            assistant = await self._assistants_repository.get_default()
            if assistant is not None:
                assistant_id = assistant.id
        except Exception:
            pass

        upsert_command = ChatUpsertCommand(
            raw_message=message,
            refined_query=refined,
            keywords=keywords,
            intent_type=intent_type,
            search_filters=search_filters,
            user_id=user_id,
            assistant_id=assistant_id,
        )
        try:
            chat_id = await self._chat_repository.upsert(upsert_command)
            past_all = await self._chat_repository.get_top_for_context(
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
            pass

        mova_user = None
        if user_id is not None:
            try:
                mova_user = await get_viewer_user_profile(user_id)
            except Exception:
                pass

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
            movie = await self._movies_repository.get_by_slug(rec.id) or await self._movies_repository.find_by_title(
                rec.title,
            )
            if movie is None:
                continue
            rows.append((movie.id, rec, rank))
        if not rows:
            return
        try:
            await self._picks_repository.save_chat_recommendations(
                chat_id=chat_id,
                user_id=context.get("user_id"),
                movie_ids=rows,
            )
            await self._refresh_chat_trend_rankings()
        except Exception:
            pass

    async def _refresh_chat_trend_rankings(self) -> None:
        try:
            await self._rankings_use_case.refresh_chat_trend_rankings()
        except Exception:
            pass

    async def _search_movies_by_intent(
        self,
        refined_query: str,
        keywords: list[str],
        *,
        intent_type: str = "mood",
        search_filters: dict | None = None,
    ) -> list:
        try:
            return await self._search_use_case.search_by_intent(
                refined_query=refined_query,
                keywords=keywords,
                intent_type=intent_type,
                search_filters=search_filters or {},
                limit=12,
            )
        except Exception:
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
        return self._chat_prompt_builder.build_prompt(
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
    ) -> ChatResponseDto:
        intro, recommendations = self._chat_prompt_builder.parse_structured_reply(raw_gemini)

        if recommendations:
            try:
                titles = [r.title for r in recommendations]
                for title in titles:
                    title_command = MovieTitleCommand(title=title)
                    await self._movies_use_case.save_title(
                        MovieTitleCreateSchema(title=title_command.title),
                    )
            except Exception:
                pass
            try:
                recommendations = await self._chat_prompt_builder.reply_service.enrich_from_db(
                    recommendations,
                )
            except Exception:
                pass

            await self._save_picks(context, recommendations)

        return ChatResponseDto(
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
    ) -> ChatResponseDto:
        context = await self.prepare_chat_context(message, user_id=user_id)
        prompt = await self.build_prompt(history, message, context=context)
        raw = gemini_reply(prompt, model_key)
        return await self.build_response(raw, context)

    async def chat_from_request(self, req: MovaChatRequest) -> ChatResponseDto:
        command = ChatMessageCommand.from_request(req)
        return await self.chat(
            command.message,
            command.history,
            user_id=command.user_id,
            model_key=command.model_key,
        )
