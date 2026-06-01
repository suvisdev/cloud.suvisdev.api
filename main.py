import asyncio
import logging
import sys
from contextlib import asynccontextmanager

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from pathlib import Path
from typing import Literal

logging.basicConfig(level=logging.INFO, format="%(levelname)s:\t%(message)s", force=True)
logger = logging.getLogger(__name__)
request_logger = logging.getLogger("uvicorn.error")

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

# 어디서 실행하든 `apps`가 모듈 루트로 잡히도록 (mova, titanic, adapters 등)
_BACKEND_ROOT = Path(__file__).resolve().parent
_APPS_ROOT = _BACKEND_ROOT / "apps"
for _p in (_BACKEND_ROOT, _APPS_ROOT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from adapters.db_health_adapter import DbHealthAdapter
from core.database import create_tables, dispose_engine, get_db, verify_connection
from doro.app.doro_director import DoroDirector
from matrix.app.keymaker import get_keymaker
from matrix.app.weather_reader import (
    WeatherReaderError,
    fetch_current_weather,
    fetch_weekly_forecast,
)
from mova.app.controllers.actors_controller import ActorsController
from mova.app.controllers.audience_controller import MovaChatController
from mova.app.controllers.movies_controller import MoviesController
from mova.app.controllers.characters_controller import CharactersController
from mova.app.controllers.tags_controller import TagsController
from mova.app.controllers.rankings_controller import RankingsController
from mova.app.controllers.search_controller import SearchController
from mova.app.controllers.movie_import_controller import MovieImportController
from mova.app.controllers.reviews_controller import ReviewsController
from mova.app.repositories.actors_repository import ActorsRepositoryError
from mova.app.repositories.movies_repository import MoviesRepositoryError
from mova.app.schemas.actors_schema import ActorCreateSchema, ActorSchema
from mova.app.schemas.audience_schema import MovaChatResponseSchema
from mova.app.schemas.mova_title_schema import MovaTitleDetailSchema
from mova.app.schemas.movies_schema import (
    MovieCreateSchema,
    MovieSchema,
    MovieTitleCreateSchema,
    MovieTitleSchema,
)
from mova.app.schemas.search_schema import MovaSearchItemSchema
from mova.app.schemas.movie_import_schema import MovieImportResultSchema
from mova.app.adapters.kofic_adapter import KoficAdapter, KoficAdapterError
from mova.app.adapters.tmdb_adapter import TmdbAdapterError
from mova.app.repositories.characters_repository import CharactersRepositoryError
from mova.app.repositories.tags_repository import TagsRepositoryError
from mova.app.repositories.rankings_repository import RankingsRepositoryError
from mova.app.schemas.characters_schema import (
    CharacterLinkCreateSchema,
    CharacterLinkSchema,
    CharacterWithActorSchema,
    CharacterWithMovieSchema,
)
from mova.app.schemas.tags_schema import (
    MoviesByTagSchema,
    TagCatalogSchema,
    TagCreateSchema,
    TagSchema,
)
from mova.app.repositories.reviews_repository import ReviewsRepositoryError
from mova.app.schemas.rankings_schema import HotRankingDisplaySchema, RankingBulkSchema
from mova.app.schemas.reviews_schema import (
    MovieRatingSummarySchema,
    ReviewActivityCreateSchema,
    ReviewActivitySchema,
    ReviewActivityWithMovieSchema,
    ReviewCreateSchema,
    ReviewSchema,
    ReviewUpdateSchema,
    ReviewWithUserSchema,
)
from friday13th.app.dtos.user_model import seed_secom_if_empty
from friday13th.adapter.inbound.api.v1.login_router import login_router
from friday13th.adapter.inbound.api.v1.signup_router import signup_router
from titanic.adapter.inbound.api import titanic_router

keymaker = get_keymaker()


class ChatRequest(BaseModel):
    """채팅 요청 본문. 사용자 메시지를 JSON으로 전달합니다."""

    message: str = Field(..., min_length=1, description="사용자 메시지")
    model: Literal["flash", "flash15", "pro"] | None = Field(
        default=None,
        description="모델 키: flash(2.5 lite), flash15(2.5 flash), pro(2.5 pro). 생략 시 .env 또는 flash15",
    )


class ChatResponse(BaseModel):
    reply: str
    refined_query: str | None = None
    keywords: list[str] = Field(default_factory=list)


class MovaChatHistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1)


class MovaChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: list[MovaChatHistoryItem] = Field(default_factory=list)
    model: Literal["flash", "flash15", "pro"] | None = None
    user_id: int | None = Field(
        default=None,
        description="Mova 사용자 ID — 선호 장르를 추천 프롬프트에 반영",
    )


class WeatherResponse(BaseModel):
    city: str
    temp_c: float
    description: str
    icon: str


class DailyForecast(BaseModel):
    date: str
    weekday: str
    temp_min: float
    temp_max: float
    description: str
    icon: str


class ForecastResponse(BaseModel):
    city: str
    days: list[DailyForecast]


class SignupRequest(BaseModel):
    username: str = Field(..., min_length=4, max_length=50, description="아이디")
    password: str = Field(..., min_length=6, max_length=128, description="비밀번호")
    nickname: str = Field(..., min_length=1, max_length=50, description="닉네임")
    email: str = Field(..., min_length=3, max_length=255, description="이메일")
    gender: str | None = Field(
        default="undisclosed",
        description="male | female | other | undisclosed",
    )
    age_group: str | None = Field(
        default="undisclosed",
        description="10s | 20s | 30s | 40s | 50s | 60s_plus | undisclosed",
    )
    birth_year: int | None = Field(default=None, ge=1900, le=2100)
    preferred_genres: list[str] = Field(default_factory=list)


class SignupResponse(BaseModel):
    message: str
    id: int
    username: str
    nickname: str
    email: str


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, description="아이디")
    password: str = Field(..., min_length=1, max_length=128, description="비밀번호")


class LoginResponse(BaseModel):
    message: str
    id: int
    username: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    from core.database import reload_env

    reload_env()
    try:
        ok, err = await verify_connection()
        if ok:
            try:
                await create_tables()
                await seed_secom_if_empty()
                try:
                    from mova.app.seed_assistants import seed_assistants_if_empty

                    await seed_assistants_if_empty()
                except Exception as ast_err:
                    logger.warning("[main] assistants 시드 생략: %s", ast_err)
                try:
                    from mova.app.services.movie_import_service import MovieImportService

                    seed_result = await MovieImportService().seed_catalog_if_sparse()
                    if seed_result:
                        logger.info(
                            "[main] TMDB 시드 완료 — imported=%s rankings=%s",
                            seed_result.imported,
                            seed_result.rankings_updated,
                        )
                except Exception as tmdb_err:
                    logger.warning("[main] TMDB 자동 시드 생략: %s", tmdb_err)
            except Exception as e:
                logger.error("DB 테이블/시드 초기화 실패 — API는 기동되며 DB 라우트는 503: %s", e)
                await dispose_engine()
        else:
            logger.warning(
                "DB 미연결 — Mova/회원 DB API 비활성. backend/.env DATABASE_URL 확인: %s",
                err,
            )
        logger.info(
            "[startup] Titanic CSV 업로드 엔드포인트: POST /titanic/james/upload",
        )
        logger.info(
            "[startup] Titanic 승객 목록 엔드포인트: GET /titanic/walter/passengers",
        )
        logger.info(
            "[startup] 회원가입 엔드포인트: POST /friday13th/signup/signup",
        )
        logger.info(
            "[startup] 로그인 엔드포인트: POST /friday13th/login/login",
        )
        yield
    finally:
        await dispose_engine()


app = FastAPI(title="Suvisdev Main Page", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_path_logger(request: Request, call_next):
    print(f"[REQ] {request.method} {request.url.path}", flush=True)
    request_logger.warning("[REQ] %s %s", request.method, request.url.path)
    response = await call_next(request)
    print(
        f"[RES] {request.method} {request.url.path} -> {response.status_code}",
        flush=True,
    )
    request_logger.warning(
        "[RES] %s %s -> %s",
        request.method,
        request.url.path,
        response.status_code,
    )
    return response

app.include_router(titanic_router)
app.include_router(login_router)
app.include_router(signup_router)


@app.get("/")
def read_root():
    return {"message": "FAST API 메인 페이지", "docs": "/docs"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """
    JSON 본문 `{"message": "...", "model": "flash|flash15|pro"}` 를 받아 Gemini 답변을 반환합니다.
    """
    if not keymaker.is_gemini_ready():
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY가 설정되지 않았습니다. backend/.env 에 키를 넣어 주세요.",
        )

    gemini = keymaker.get_gemini_model(req.model)
    if gemini is None:
        raise HTTPException(status_code=503, detail="Gemini 모델을 초기화할 수 없습니다.")

    try:
        response = gemini.generate_content(req.message)
    except Exception as e:
        err = str(e)
        if "429" in err or "quota" in err.lower() or "resource_exhausted" in err.lower():
            raise HTTPException(
                status_code=429,
                detail=(
                    "Gemini 무료 사용 한도에 도달했습니다. "
                    "약 1분 후 다시 시도하거나, 모델을 '빠른 모델'로 선택해 주세요."
                ),
            ) from e
        if "404" in err and "not found" in err.lower():
            raise HTTPException(
                status_code=400,
                detail=(
                    "요청한 Gemini 모델을 찾을 수 없습니다. "
                    "모델 선택을 Flash 2.5(권장) 또는 빠른 모델로 바꾼 뒤 다시 시도해 주세요."
                ),
            ) from e
        raise HTTPException(
            status_code=502,
            detail=f"Gemini 호출 실패: {e!s}",
        ) from e

    try:
        text = (response.text or "").strip()
    except ValueError as e:
        feedback = getattr(response, "prompt_feedback", None)
        raise HTTPException(
            status_code=400,
            detail=f"응답 텍스트를 읽을 수 없습니다: {e!s}. prompt_feedback={feedback}",
        ) from e

    if not text:
        reason = None
        if getattr(response, "candidates", None):
            c0 = response.candidates[0]
            reason = getattr(c0, "finish_reason", None)
        raise HTTPException(
            status_code=502,
            detail=(
                "모델이 비어 있는 응답을 반환했습니다."
                + (f" (finish_reason={reason})" if reason else "")
            ),
        )

    return ChatResponse(reply=text)


@app.get("/weather", response_model=WeatherResponse)
async def read_weather(city: str | None = None) -> WeatherResponse:
    """OpenWeatherMap 현재 날씨. API 키는 backend/.env 에만 둡니다."""
    keymaker.reload_openweather_env()

    if not keymaker.is_openweather_ready():
        raise HTTPException(
            status_code=503,
            detail="OPENWEATHERMAP_API_KEY가 설정되지 않았습니다. backend/.env 에 키를 넣어 주세요.",
        )

    target_city = (city or keymaker.openweather_city or "Seoul").strip()
    if not target_city:
        raise HTTPException(status_code=400, detail="도시 이름이 비어 있습니다.")

    try:
        data = await fetch_current_weather(
            city=target_city,
            api_key=keymaker.openweather_api_key,
        )
    except WeatherReaderError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e

    return WeatherResponse(**data)  # type: ignore[arg-type]


@app.get("/weather/forecast", response_model=ForecastResponse)
async def read_weather_forecast(city: str | None = None) -> ForecastResponse:
    """일별 5일 예보 (OpenWeatherMap 5일/3시간 API)."""
    keymaker.reload_openweather_env()

    if not keymaker.is_openweather_ready():
        raise HTTPException(
            status_code=503,
            detail="OPENWEATHERMAP_API_KEY가 설정되지 않았습니다. backend/.env 에 키를 넣어 주세요.",
        )

    target_city = (city or keymaker.openweather_city or "Seoul").strip()
    if not target_city:
        raise HTTPException(status_code=400, detail="도시 이름이 비어 있습니다.")

    try:
        data = await fetch_weekly_forecast(
            city=target_city,
            api_key=keymaker.openweather_api_key,
        )
    except WeatherReaderError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e

    return ForecastResponse(**data)  # type: ignore[arg-type]


def _gemini_reply(prompt: str, model_key: Literal["flash", "flash15", "pro"] | None) -> str:
    if not keymaker.is_gemini_ready():
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY가 설정되지 않았습니다. backend/.env 에 키를 넣어 주세요.",
        )
    gemini = keymaker.get_gemini_model(model_key)
    if gemini is None:
        raise HTTPException(status_code=503, detail="Gemini 모델을 초기화할 수 없습니다.")
    try:
        response = gemini.generate_content(prompt)
    except Exception as e:
        err = str(e)
        if "429" in err or "quota" in err.lower() or "resource_exhausted" in err.lower():
            raise HTTPException(
                status_code=429,
                detail="Gemini 사용 한도에 도달했습니다. 잠시 후 다시 시도해 주세요.",
            ) from e
        raise HTTPException(status_code=502, detail=f"Gemini 호출 실패: {e!s}") from e
    try:
        text = (response.text or "").strip()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"응답을 읽을 수 없습니다: {e!s}") from e
    if not text:
        raise HTTPException(status_code=502, detail="모델이 비어 있는 응답을 반환했습니다.")
    return text


@app.post("/mova/reviews/activity", response_model=ReviewActivitySchema, status_code=201)
async def mova_record_review_activity(
    req: ReviewActivityCreateSchema,
) -> ReviewActivitySchema:
    """사용자 영화 반응 (`reviews` 테이블) — 찜/시청/클릭/관심없음. 별점 리뷰는 POST /mova/reviews."""
    logger.info(
        "[main] mova review activity — user=%s movie=%s %s",
        req.user_id,
        req.movie_id,
        req.action_type,
    )
    try:
        return await ReviewsController().record_activity(req)
    except ReviewsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get("/mova/reviews/activity", response_model=list[ReviewActivitySchema])
async def mova_list_review_activities(
    user_id: int,
    action_type: str | None = None,
    limit: int = 100,
) -> list[ReviewActivitySchema]:
    """사용자 반응 이력 (별점 리뷰 제외)."""
    try:
        return await ReviewsController().list_activities_by_user(
            user_id,
            action_type=action_type,
            limit=limit,
        )
    except ReviewsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get(
    "/mova/users/{user_id}/reviews/activity",
    response_model=list[ReviewActivityWithMovieSchema],
)
async def mova_list_user_review_activities(
    user_id: int,
    action_type: str | None = None,
    limit: int = 100,
) -> list[ReviewActivityWithMovieSchema]:
    """사용자 반응 + 영화 제목 (취향 분석·대시보드용)."""
    try:
        return await ReviewsController().list_activities_by_user(
            user_id,
            action_type=action_type,
            limit=limit,
            with_movies=True,
        )
    except ReviewsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.post("/mova/reviews", response_model=ReviewSchema, status_code=201)
async def mova_save_review(req: ReviewCreateSchema) -> ReviewSchema:
    """영화 별점·감상평 (`reviews`, action_type=review) — 평균 별점 자동 갱신."""
    logger.info("[main] mova review — user=%s movie=%s", req.user_id, req.movie_id)
    try:
        return await ReviewsController().save_rating_review(req)
    except ReviewsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.patch("/mova/reviews/{review_id}", response_model=ReviewSchema)
async def mova_update_review(review_id: int, req: ReviewUpdateSchema) -> ReviewSchema:
    try:
        return await ReviewsController().update_rating_review(review_id, req)
    except ReviewsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get("/mova/reviews", response_model=list[ReviewSchema])
async def mova_list_reviews(
    user_id: int | None = None,
    movie_id: int | None = None,
    limit: int = 50,
) -> list[ReviewSchema]:
    """리뷰 목록 (user_id 또는 movie_id 필수)."""
    if user_id is None and movie_id is None:
        raise HTTPException(status_code=400, detail="user_id 또는 movie_id가 필요합니다.")
    try:
        if user_id is not None:
            return await ReviewsController().list_rating_reviews_by_user(
                user_id,
                limit=limit,
            )
        return await ReviewsController().list_rating_reviews_by_movie(
            movie_id,
            limit=limit,
        )
    except ReviewsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get(
    "/mova/movies/{movie_id}/reviews",
    response_model=list[ReviewWithUserSchema],
)
async def mova_list_movie_reviews(
    movie_id: int,
    limit: int = 50,
) -> list[ReviewWithUserSchema]:
    """영화 리뷰 목록 (닉네임 포함 — 커뮤니티 UI)."""
    try:
        return await ReviewsController().list_rating_reviews_by_movie_with_users(
            movie_id,
            limit=limit,
        )
    except ReviewsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get(
    "/mova/movies/{movie_id}/rating-summary",
    response_model=MovieRatingSummarySchema,
)
async def mova_movie_rating_summary(movie_id: int) -> MovieRatingSummarySchema:
    """영화 평균 별점·리뷰 수 (랭킹 ★4.5 표시용)."""
    try:
        return await ReviewsController().get_movie_rating_summary(movie_id)
    except ReviewsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.post("/mova/chat", response_model=MovaChatResponseSchema)
async def mova_chat(req: MovaChatRequest) -> MovaChatResponseSchema:
    """Mova AI 영화 추천 채팅 → 의도 추출·DB 저장(선택)·3편 구조화 추천."""
    logger.info("[main] mova chat 진입 — message_len=%s", len(req.message))
    message = req.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="message가 비어 있습니다.")
    history = [{"role": h.role, "content": h.content} for h in req.history]
    controller = MovaChatController()
    try:
        context = await controller.prepare_chat_context(message, user_id=req.user_id)
        prompt = await controller.build_prompt(history, message, context=context)
        raw = _gemini_reply(prompt, req.model)
        return await controller.build_response(raw, context)
    except HTTPException:
        raise
    except RuntimeError as e:
        if "GEMINI" in str(e).upper() or "API_KEY" in str(e).upper():
            raise HTTPException(status_code=503, detail=str(e)) from e
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        logger.exception("[main] mova chat 실패")
        raise HTTPException(
            status_code=502,
            detail="추천을 생성하지 못했습니다. 잠시 후 다시 시도해 주세요.",
        ) from e


@app.get("/mova/search", response_model=list[MovaSearchItemSchema])
async def mova_search(q: str = "", limit: int = 12) -> list[MovaSearchItemSchema]:
    """작품·인물·키워드(태그·장르) 통합 검색 — DB `movies` 등 연동."""
    query = q.strip()
    if not query:
        return []
    capped = min(max(limit, 1), 50)
    try:
        return await SearchController().search(query, limit=capped)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get("/mova/titles/{slug}", response_model=MovaTitleDetailSchema)
async def mova_get_title_by_slug(slug: str) -> MovaTitleDetailSchema:
    """slug 기준 영화 상세 (검색 결과 → 상세 페이지)."""
    try:
        return await MoviesController().get_title_by_slug(slug)
    except MoviesRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.post("/mova/movies", response_model=MovieSchema, status_code=201)
async def mova_save_movie(req: MovieCreateSchema) -> MovieSchema:
    """영화 정보 저장 (`movies`)."""
    logger.info("[main] mova save movie — %r", req.title)
    try:
        return await MoviesController().save_movie(req)
    except MoviesRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get("/mova/movies", response_model=list[MovieSchema])
async def mova_list_movies(limit: int = 100) -> list[MovieSchema]:
    """영화 목록."""
    try:
        return await MoviesController().list_movies(limit=limit)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.post("/mova/movies/titles", response_model=MovieTitleSchema, status_code=201)
async def mova_save_movie_title(req: MovieTitleCreateSchema) -> MovieTitleSchema:
    """영화 제목만 저장 (채팅 추천 등 하위 호환)."""
    logger.info("[main] mova save movie title — %r", req.title)
    try:
        return await MoviesController().save_title(req)
    except MoviesRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get("/mova/movies/titles", response_model=list[MovieTitleSchema])
async def mova_list_movie_titles(limit: int = 100) -> list[MovieTitleSchema]:
    """저장된 영화 제목 목록 (하위 호환)."""
    try:
        return await MoviesController().list_titles(limit=limit)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get("/mova/movies/{movie_id}", response_model=MovieSchema)
async def mova_get_movie(movie_id: int) -> MovieSchema:
    """영화 단건 조회."""
    try:
        return await MoviesController().get_movie(movie_id)
    except MoviesRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.post("/mova/actors", response_model=ActorSchema, status_code=201)
async def mova_save_actor(req: ActorCreateSchema) -> ActorSchema:
    """인물(감독·배우) 정보 저장 (`actors`)."""
    logger.info("[main] mova save actor — %r", req.name)
    try:
        return await ActorsController().save_actor(req)
    except ActorsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get("/mova/actors", response_model=list[ActorSchema])
async def mova_list_actors(limit: int = 100) -> list[ActorSchema]:
    """인물 목록."""
    try:
        return await ActorsController().list_actors(limit=limit)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.post("/mova/actors/names", response_model=ActorSchema, status_code=201)
async def mova_save_actor_name(req: ActorCreateSchema) -> ActorSchema:
    """배우 이름만 저장 (하위 호환, role_type=actor)."""
    logger.info("[main] mova save actor name — %r", req.name)
    try:
        return await ActorsController().save_name(req)
    except ActorsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get("/mova/actors/names", response_model=list[ActorSchema])
async def mova_list_actor_names(limit: int = 100) -> list[ActorSchema]:
    """저장된 인물 목록 (하위 호환)."""
    try:
        return await ActorsController().list_names(limit=limit)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get("/mova/actors/{actor_id}", response_model=ActorSchema)
async def mova_get_actor(actor_id: int) -> ActorSchema:
    """인물 단건 조회."""
    try:
        return await ActorsController().get_actor(actor_id)
    except ActorsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.post("/mova/characters", response_model=CharacterLinkSchema, status_code=201)
async def mova_link_character(
    req: CharacterLinkCreateSchema,
) -> CharacterLinkSchema:
    """영화–인물(배우) 연결 저장 (`characters`)."""
    logger.info("[main] mova link character — movie_id=%s actor_id=%s", req.movie_id, req.actor_id)
    try:
        return await CharactersController().link(req)
    except CharactersRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.delete("/mova/characters/{link_id}", status_code=204)
async def mova_unlink_character(link_id: int) -> None:
    """영화–인물 연결 삭제."""
    try:
        await CharactersController().unlink(link_id)
    except CharactersRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get("/mova/characters", response_model=list[CharacterLinkSchema])
async def mova_list_character_links(
    movie_id: int | None = None,
    actor_id: int | None = None,
    limit: int = 100,
) -> list[CharacterLinkSchema]:
    """연결 목록 (movie_id 또는 actor_id로 필터 가능)."""
    try:
        return await CharactersController().list_links(
            movie_id=movie_id,
            actor_id=actor_id,
            limit=limit,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get(
    "/mova/movies/{movie_id}/characters",
    response_model=list[CharacterWithActorSchema],
)
async def mova_list_characters_by_movie(
    movie_id: int,
    limit: int = 100,
) -> list[CharacterWithActorSchema]:
    """영화에 출연한 인물(배우) 목록."""
    try:
        return await CharactersController().list_actors_by_movie(movie_id, limit=limit)
    except CharactersRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get(
    "/mova/actors/{actor_id}/movies",
    response_model=list[CharacterWithMovieSchema],
)
async def mova_list_movies_by_actor(
    actor_id: int,
    limit: int = 100,
) -> list[CharacterWithMovieSchema]:
    """인물(배우)가 출연한 영화 목록."""
    try:
        return await CharactersController().list_movies_by_actor(actor_id, limit=limit)
    except CharactersRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.post("/mova/tags", response_model=TagSchema, status_code=201)
async def mova_attach_tag(req: TagCreateSchema) -> TagSchema:
    """영화에 감성 태그 붙이기 (`tags` 테이블)."""
    logger.info(
        "[main] mova attach tag — movie_id=%s %r",
        req.movie_id,
        req.label,
    )
    try:
        return await TagsController().attach(req)
    except TagsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get("/mova/tags/catalog", response_model=list[TagCatalogSchema])
async def mova_list_tag_catalog(limit: int = 100) -> list[TagCatalogSchema]:
    """slug 기준 감성 태그 카탈로그 (채팅 버튼 등)."""
    try:
        return await TagsController().list_catalog(limit=limit)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.delete("/mova/tags/{link_id}", status_code=204)
async def mova_unlink_tag(link_id: int) -> None:
    try:
        await TagsController().unlink(link_id)
    except TagsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get("/mova/movies/{movie_id}/tags", response_model=list[TagSchema])
async def mova_list_tags_by_movie(movie_id: int, limit: int = 50) -> list[TagSchema]:
    """영화에 붙은 감성 태그."""
    try:
        return await TagsController().list_by_movie(movie_id, limit=limit)
    except TagsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get("/mova/tags/{slug}/movies", response_model=list[MoviesByTagSchema])
async def mova_list_movies_by_tag_slug(slug: str, limit: int = 50) -> list[MoviesByTagSchema]:
    """slug에 해당하는 영화 목록."""
    try:
        return await TagsController().list_movies_by_slug(slug, limit=limit)
    except TagsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.post("/mova/import/tmdb/popular", response_model=MovieImportResultSchema)
async def mova_import_tmdb_popular(
    pages: int = 2,
    setup_rankings: bool = True,
) -> MovieImportResultSchema:
    """TMDB 인기 영화를 DB에 적재하고 HOT 랭킹을 갱신한다."""
    try:
        return await MovieImportController().import_popular(
            pages=min(max(pages, 1), 5),
            setup_rankings=setup_rankings,
        )
    except TmdbAdapterError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.post("/mova/import/tmdb/search", response_model=MovieImportResultSchema)
async def mova_import_tmdb_search(
    q: str,
    pages: int = 1,
    setup_rankings: bool = False,
) -> MovieImportResultSchema:
    """TMDB 검색 결과를 DB에 적재한다."""
    query = q.strip()
    if not query:
        raise HTTPException(status_code=400, detail="검색어 q가 비어 있습니다.")
    try:
        return await MovieImportController().import_search(
            query,
            pages=min(max(pages, 1), 3),
            setup_rankings=setup_rankings,
        )
    except TmdbAdapterError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.post("/mova/import/tmdb/movie/{tmdb_id}", response_model=MovieImportResultSchema)
async def mova_import_tmdb_movie(tmdb_id: int) -> MovieImportResultSchema:
    """TMDB 영화 ID 한 편을 DB에 적재한다."""
    try:
        return await MovieImportController().import_by_tmdb_id(tmdb_id)
    except TmdbAdapterError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


def _validate_kofic_target_date(raw: str) -> str:
    value = raw.strip()
    if len(value) != 8 or not value.isdigit():
        raise HTTPException(status_code=400, detail="target_date 형식은 YYYYMMDD 입니다.")
    return value


@app.post("/mova/import/kofic/daily", response_model=MovieImportResultSchema)
async def mova_import_kofic_daily(
    target_date: str | None = None,
    setup_rankings: bool = True,
) -> MovieImportResultSchema:
    """KOFIC 일간 박스오피스를 DB에 적재하고 HOT 랭킹을 갱신한다."""
    date_arg = _validate_kofic_target_date(target_date or KoficAdapter.default_target_date())
    try:
        return await MovieImportController().import_kofic_daily(
            target_date=date_arg,
            setup_rankings=setup_rankings,
        )
    except KoficAdapterError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.post("/mova/import/kofic/weekly", response_model=MovieImportResultSchema)
async def mova_import_kofic_weekly(
    target_date: str | None = None,
    week_gb: str = "0",
    setup_rankings: bool = True,
) -> MovieImportResultSchema:
    """KOFIC 주간/주말 박스오피스를 DB에 적재하고 HOT 랭킹을 갱신한다."""
    date_arg = _validate_kofic_target_date(target_date or KoficAdapter.default_target_date())
    if week_gb not in ("0", "1"):
        raise HTTPException(status_code=400, detail="week_gb는 0(주간) 또는 1(주말)이어야 합니다.")
    try:
        return await MovieImportController().import_kofic_weekly(
            target_date=date_arg,
            week_gb=week_gb,
            setup_rankings=setup_rankings,
        )
    except KoficAdapterError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.post("/mova/import/enrich-posters", response_model=MovieImportResultSchema)
async def mova_enrich_missing_posters(limit: int = 30) -> MovieImportResultSchema:
    """포스터가 비어 있는 영화에 TMDB 포스터 URL을 채운다 (KOFIC 연동 보강)."""
    try:
        return await MovieImportController().enrich_missing_posters(
            limit=min(max(limit, 1), 100),
        )
    except TmdbAdapterError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.post("/mova/import/kofic/movie/{movie_cd}", response_model=MovieImportResultSchema)
async def mova_import_kofic_movie(movie_cd: str) -> MovieImportResultSchema:
    """KOFIC 영화코드 한 편을 DB에 적재한다."""
    code = movie_cd.strip()
    if not code:
        raise HTTPException(status_code=400, detail="movie_cd가 비어 있습니다.")
    try:
        return await MovieImportController().import_by_kofic_cd(code)
    except KoficAdapterError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get("/mova/rankings/hot", response_model=list[HotRankingDisplaySchema])
async def mova_list_hot_rankings(
    limit: int = 20,
    ranked_at: str | None = None,
) -> list[HotRankingDisplaySchema]:
    """Mova HOT 랭킹 (최신 기준일 또는 ranked_at=YYYY-MM-DD)."""
    from datetime import date as date_type

    parsed_date = None
    if ranked_at:
        try:
            parsed_date = date_type.fromisoformat(ranked_at)
        except ValueError as e:
            raise HTTPException(status_code=400, detail="ranked_at 형식은 YYYY-MM-DD 입니다.") from e
    try:
        return await RankingsController().list_hot_rankings(
            ranked_at=parsed_date,
            limit=limit,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e

@app.get("/db-check")
async def check_db(db: AsyncSession = Depends(get_db)):
    return await DbHealthAdapter.neon_time_check(db)


@app.get("/db-check/domains")
async def check_db_domains(db: AsyncSession = Depends(get_db)):
    """Mova·Secom 테이블 접근 확인."""
    return await DbHealthAdapter.check_all_domains(db)


@app.get("/doro/data")
def read_doro_data():
    raise HTTPException(
        status_code=410,
        detail="프로젝트 내부 파일 읽기 기능이 제거되었습니다. 외부 저장소/DB 연동으로 전환해 주세요.",
    )

if __name__ == "__main__":
    import selectors
    import uvicorn

    config = uvicorn.Config(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True,
    )
    server = uvicorn.Server(config)
    if sys.platform == "win32":
        # psycopg async는 ProactorEventLoop와 충돌하므로 Selector 루프를 강제한다.
        with asyncio.Runner(
            loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector()),
        ) as runner:
            runner.run(server.serve())
    else:
        asyncio.run(server.serve())

# 회원가입
