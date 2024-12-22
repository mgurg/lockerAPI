import sys
from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sentry_sdk

from app.config import get_settings
from app.controller.companies import company_router
from app.controller.games import game_router
from app.controller.places import place_router
from app.controller.rooms import room_router

settings = get_settings()

logger.add("logs/locker_api.log", format="{time} {level} {message}", level=settings.LOG_LEVEL, backtrace=False, diagnose=False)
logger.add(sys.stderr, format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", level=settings.LOG_LEVEL)

origins: list[str] = ["http://localhost:3000", settings.APP_URL]


def create_application() -> FastAPI:
    """
    Create base FastAPI app with CORS middlewares and routes loaded
    Returns:
        FastAPI: [description]
    """
    app = FastAPI(debug=False, openapi_url=settings.APP_API_DOCS)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["*"],
        max_age=86400,
    )

    app.include_router(room_router, prefix="/rooms", tags=["ROOM"])
    app.include_router(place_router, prefix="/places", tags=["PLACE"])
    app.include_router(company_router, prefix="/companies", tags=["COMPANY"])
    app.include_router(game_router, prefix="/games", tags=["GAMES"])

    return app

app = create_application()

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    _experiments={
        # Set continuous_profiling_auto_start to True
        # to automatically start the profiler on when
        # possible.
        "continuous_profiling_auto_start": True,
    },
)


@app.get("/")
async def read_root():
    return {"Hello": "World!", "env": settings.ENVIRONMENT, "time": datetime.now(UTC), "appUrl": settings.APP_URL}
