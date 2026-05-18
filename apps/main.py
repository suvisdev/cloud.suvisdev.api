import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

logging.basicConfig(level=logging.INFO, format="%(levelname)s:\t%(message)s")
logger = logging.getLogger(__name__)

from fastapi import Depends, FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

# 어디서 실행하든 `apps`가 모듈 루트로 잡히도록 (adapters, database, titanic 등)
_APPS_ROOT = Path(__file__).resolve().parent
if str(_APPS_ROOT) not in sys.path:
    sys.path.insert(0, str(_APPS_ROOT))

from adapters.db_health_adapter import DbHealthAdapter
from database import dispose_engine, get_db
from doro.app.doro_director import DoroDirector
from matrix.app.keymaker import get_keymaker
from matrix.app.weather_reader import (
    WeatherReaderError,
    fetch_current_weather,
    fetch_weekly_forecast,
)
from secom.app.controllers.user_controller import UserController
from secom.app.schemas.user_schema import UserSchema
from titanic.app.james_controller import JamesController

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


class SignupResponse(BaseModel):
    message: str
    username: str
    nickname: str
    email: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
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


@app.post("/auth/signup", response_model=SignupResponse, status_code=201)
def signup(req: SignupRequest) -> SignupResponse:
    """회원가입 JSON 수신 후 서버 로그에 기록한다."""
    username = req.username.strip()
    nickname = req.nickname.strip()
    email = req.email.strip()

    logger.info(
        "회원가입 수신 — 아이디: %s | 비밀번호: %s | 닉네임: %s | 이메일: %s",
        req.username,
        req.password,
        req.nickname,
        req.email,
    )
# 프론트엔드에서 가져온 데이터를 스키마에 담아서 DB로 보내는 코드
    user_schema = UserSchema(
        username=req.username, 
        password=req.password, 
        nickname=req.nickname, 
        email=req.email, 
        role="user")

    user_controller = UserController()
    user_controller.save_user(user_schema)
    
    return SignupResponse(
        message="회원가입 요청이 접수되었습니다.",
        username=req.username,
        nickname=req.nickname,
        email=req.email,
    )


@app.get("/db-check")
async def check_db(db: AsyncSession = Depends(get_db)):
    return await DbHealthAdapter.neon_time_check(db)


@app.get("/titanic/data")
def read_titanic_data():
    james = JamesController()
    df = james.get_data()
    return df.to_dict(orient="records")


@app.get("/titanic/count")
def read_titanic_count():
    james = JamesController()
    count = james.get_count()
    return {"count": count}


@app.get("/titanic/count/survived")
def read_titanic_count_survived():
    james = JamesController()
    survived_count = james.get_survived_count()
    return {"survived_count": survived_count}


@app.get("/titanic/count/dead")
def read_titanic_count_dead():
    james = JamesController()
    dead_count = james.get_dead_count()
    return {"dead_count": dead_count}


@app.get("/titanic/dead/count")
def read_titanic_dead_count():
    james = JamesController()
    dead_count = james.get_dead_count()
    return {"dead_count": dead_count}


@app.get("/titanic/tree")
def read_titanic_tree():
    james = JamesController()
    tree = james.has_decision_tree_model()
    return {"tree": tree}


@app.get("/titanic/model")
def read_titanic_model():
    controller = JamesController()
    model_name = controller.get_model_name_and_accuracy()
    return JSONResponse(content=jsonable_encoder(model_name))


@app.get("/doro/data")
def read_doro_data():
    doro_director = DoroDirector()
    df = doro_director.get_data()
    return df.to_dict(orient="records")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

# 회원가입
