import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.basicConfig(level=logging.INFO, format="%(levelname)s:\t%(message)s", force=True)
logger = logging.getLogger(__name__)

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

_BACKEND_ROOT = Path(__file__).resolve().parent
_APPS_ROOT = _BACKEND_ROOT / "apps"
for _p in (_BACKEND_ROOT, _APPS_ROOT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from adapters.db_health_adapter import DbHealthAdapter
from core.matrix.keymaker_api import get_keymaker
from core.matrix.oracle_database import create_tables, dispose_engine, get_db, verify_connection
from core.matrix.weather_reader import (
    WeatherReaderError,
    fetch_current_weather,
    fetch_weekly_forecast,
)
from viewer.adapter.inbound.api import login_router, signup_router
from viewer.app.dtos.user_model import seed_secom_if_empty
from mova.adapter.inbound.api import mova_router
from mova.adapter.inbound.api.gemini_reply import gemini_reply
from titanic.adapter.inbound.api import titanic_router

keymaker = get_keymaker()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="??? ???")
    model: Literal["flash", "flash15", "pro"] | None = Field(
        default=None,
        description="Gemini ?? ? (??? ? .env ???)",
    )


class ChatResponse(BaseModel):
    reply: str
    refined_query: str | None = None
    keywords: list[str] = Field(default_factory=list)


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


def _resolve_weather_city(city: str | None) -> str:
    target = (city or keymaker.openweather_city or "Seoul").strip()
    if not target:
        raise HTTPException(status_code=400, detail="?? ??? ?? ????.")
    return target


@asynccontextmanager
async def lifespan(app: FastAPI):
    from core.matrix.oracle_database import reload_env

    reload_env()
    try:
        ok, err = await verify_connection()
        if ok:
            try:
                await create_tables()
                await seed_secom_if_empty()
                try:
                    from mova.adapter.outbound.pg.assistants_pg_repository import (
                        seed_assistants_if_empty,
                    )

                    await seed_assistants_if_empty()
                except Exception as ast_err:
                    logger.warning("[main] assistants ?? ??: %s", ast_err)
                try:
                    from mova.app.use_cases.movie_import_interactor import MovieImportInteractor

                    seed_result = await MovieImportInteractor().seed_catalog_if_sparse()
                    if seed_result:
                        logger.info(
                            "[main] TMDB ?? ?? ? imported=%s rankings=%s",
                            seed_result.imported,
                            seed_result.rankings_updated,
                        )
                except Exception as tmdb_err:
                    logger.warning("[main] TMDB ?? ?? ??: %s", tmdb_err)
            except Exception as e:
                logger.error(
                    "DB ???/?? ??? ?? ? DB ?? API? 503 ??: %s",
                    e,
                )
                await dispose_engine()
        else:
            logger.warning(
                "DB ?? ?? ? Mova/Secom DB API ???. backend/.env DATABASE_URL ??: %s",
                err,
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
    response = await call_next(request)
    logger.info(
        "%s %s -> %s",
        request.method,
        request.url.path,
        response.status_code,
    )
    return response


app.include_router(mova_router)
app.include_router(titanic_router)
app.include_router(login_router)
app.include_router(signup_router)


@app.get("/")
def read_root():
    return {"message": "FAST API ??? ??", "docs": "/docs"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """?? Gemini ?? (?? ?? ? Mova ??? ??)."""
    text = gemini_reply(req.message, req.model)
    return ChatResponse(reply=text)


@app.get("/weather", response_model=WeatherResponse)
async def read_weather(city: str | None = None) -> WeatherResponse:
    keymaker.reload_openweather_env()
    if not keymaker.is_openweather_ready():
        raise HTTPException(
            status_code=503,
            detail="OPENWEATHERMAP_API_KEY? ???? ?????. backend/.env ? ?????.",
        )
    try:
        data = await fetch_current_weather(
            city=_resolve_weather_city(city),
            api_key=keymaker.openweather_api_key,
        )
    except WeatherReaderError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
    return WeatherResponse(**data)  # type: ignore[arg-type]


@app.get("/weather/forecast", response_model=ForecastResponse)
async def read_weather_forecast(city: str | None = None) -> ForecastResponse:
    keymaker.reload_openweather_env()
    if not keymaker.is_openweather_ready():
        raise HTTPException(
            status_code=503,
            detail="OPENWEATHERMAP_API_KEY? ???? ?????. backend/.env ? ?????.",
        )
    try:
        data = await fetch_weekly_forecast(
            city=_resolve_weather_city(city),
            api_key=keymaker.openweather_api_key,
        )
    except WeatherReaderError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
    return ForecastResponse(**data)  # type: ignore[arg-type]


@app.get("/db-check")
async def check_db(db: AsyncSession = Depends(get_db)):
    return await DbHealthAdapter.neon_time_check(db)


@app.get("/db-check/domains")
async def check_db_domains(db: AsyncSession = Depends(get_db)):
    """Mova and Secom per-domain DB health check."""
    return await DbHealthAdapter.check_all_domains(db)


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
        with asyncio.Runner(
            loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector()),
        ) as runner:
            runner.run(server.serve())
    else:
        asyncio.run(server.serve())
