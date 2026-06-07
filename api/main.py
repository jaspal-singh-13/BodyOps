"""FastAPI application entry point."""
import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import LoginRequest, TokenResponse, login
from .routers.settings import router as settings_router
from .sheets.sheets_client import get_main_sheet

logger = logging.getLogger("bodyops")
logging.basicConfig(level=logging.INFO)

REQUIRED_ENV_VARS = [
    "GOOGLE_SERVICE_ACCOUNT_JSON",
    "GOOGLE_SPREADSHEET_ID",
    "GOOGLE_AUTH_SHEET_ID",
    "JWT_SECRET",
]


VERSION = "0.2.0"


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("BodyOps API v%s starting...", VERSION)

    missing = [v for v in REQUIRED_ENV_VARS if not os.environ.get(v)]
    if missing:
        logger.error("Missing required env vars: %s", ", ".join(missing))
    else:
        logger.info("Env vars: OK")

    sheets_ok = False
    try:
        get_main_sheet()
        sheets_ok = True
    except Exception as e:
        logger.error("Google Sheets: FAILED — %s", e)

    logger.info(
        "Health: { ok: %s, sheets: %s, drive: %s }",
        sheets_ok,
        sheets_ok,
        sheets_ok,
    )
    logger.info("BodyOps API v%s ready", VERSION)
    yield
    logger.info("BodyOps API shutting down")


app = FastAPI(title="BodyOps API", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(settings_router)


@app.post("/auth/login", response_model=TokenResponse)
async def login_endpoint(body: LoginRequest) -> TokenResponse:
    return await login(body)


@app.get("/health")
async def health() -> dict:
    sheets_ok = False
    drive_ok = False
    try:
        get_main_sheet()
        sheets_ok = True
        drive_ok = True  # same service account covers Drive
    except Exception:
        pass
    return {"ok": sheets_ok and drive_ok, "sheets": sheets_ok, "drive": drive_ok}
