from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.oracle_database import get_db
from fastapi import Depends

from mova.adapter.outbound.llm.intent_extraction import IntentExtractionService
from mova.adapter.outbound.llm.chat_prompt import ChatPromptBuilder
from mova.adapter.outbound.pg.assistants_pg_repository import AssistantsPgRepository
from mova.adapter.outbound.pg.chat_pg_repository import ChatPgRepository
from mova.adapter.outbound.pg.movies_pg_repository import MoviesPgRepository
from mova.adapter.outbound.pg.picks_pg_repository import PicksPgRepository
from mova.app.ports.input.chat_use_case import ChatUseCase
from mova.app.ports.input.movies_use_case import MoviesUseCase
from mova.app.ports.input.rankings_use_case import RankingsUseCase
from mova.app.ports.input.search_use_case import SearchUseCase
from mova.app.ports.output.assistants_repository import AssistantsRepository
from mova.app.ports.output.chat_repository import ChatRepository
from mova.app.ports.output.movies_repository import MoviesRepository
from mova.app.ports.output.picks_repository import PicksRepository
from mova.app.use_cases.chat_interactor import ChatInteractor
from mova.dependencies.movies_provider import get_movies_use_case
from mova.dependencies.rankings_provider import get_rankings_use_case
from mova.dependencies.search_provider import get_search_use_case


def get_chat_use_case(
    db: AsyncSession = Depends(get_db),
    movies_use_case: MoviesUseCase = Depends(get_movies_use_case),
    search_use_case: SearchUseCase = Depends(get_search_use_case),
    rankings_use_case: RankingsUseCase = Depends(get_rankings_use_case),
) -> ChatUseCase:
    chat_repository: ChatRepository = ChatPgRepository(session=db)
    picks_repository: PicksRepository = PicksPgRepository(session=db)
    movies_repository: MoviesRepository = MoviesPgRepository(session=db)
    assistants_repository: AssistantsRepository = AssistantsPgRepository(session=db)
    return ChatInteractor(
        chat_repository=chat_repository,
        picks_repository=picks_repository,
        movies_repository=movies_repository,
        assistants_repository=assistants_repository,
        movies_use_case=movies_use_case,
        search_use_case=search_use_case,
        rankings_use_case=rankings_use_case,
        intent_extraction_service=IntentExtractionService(),
        chat_prompt_builder=ChatPromptBuilder(),
    )
