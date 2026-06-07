"""FastAPI application entry point."""
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import LoginRequest, TokenResponse, login
from .logger import get_logger
from .routers.agent import router as agent_router
from .routers.settings import router as settings_router
from .routers.weight import router as weight_router
from .sheets.sheets_client import get_main_sheet

logger = get_logger("main")

REQUIRED_ENV_VARS = [
    "GOOGLE_SERVICE_ACCOUNT_JSON",
    "GOOGLE_SPREADSHEET_ID",
    "GOOGLE_AUTH_SHEET_ID",
    "JWT_SECRET",
]

AGENT_ENV_VARS = ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_DEPLOYMENT"]

VERSION = "0.5.0"


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("BodyOps API v%s starting...", VERSION)

    missing = [v for v in REQUIRED_ENV_VARS if not os.environ.get(v)]
    if missing:
        logger.error("Missing required env vars: %s", ", ".join(missing))
    else:
        logger.info("Env vars: OK")

    missing_agent = [v for v in AGENT_ENV_VARS if not os.environ.get(v)]
    if missing_agent:
        logger.warning("Agent env vars not set (agent endpoints will fail): %s", ", ".join(missing_agent))

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


app = FastAPI(title="BodyOps API", version="0.5.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(settings_router)
app.include_router(weight_router)
app.include_router(agent_router)


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
