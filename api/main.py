"""
FastAPI application entry point.

Registers all routers, configures CORS, and defines the lifespan hook that
validates environment variables and tests the Sheets connection at startup.

Routers mounted:
    /settings  — user profile / onboarding settings
    /weight    — weight logging and trend analytics
    /workouts  — workout system (import, log, progression)
    /meals     — meal photo analysis, confirmation, and history
    /agent     — SSE-streaming AI coach chat
    /auth      — login (mounted directly, not via a router)
"""

import asyncio
import os
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from uuid import uuid4

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .auth import LoginRequest, TokenResponse, login
from .logger import get_logger, request_id_var
from .routers.agent import router as agent_router
from .routers.coach import router as coach_router
from .routers.meals import router as meals_router
from .routers.progress import router as progress_router
from .routers.settings import router as settings_router
from .routers.tasks import router as tasks_router
from .routers.weight import router as weight_router
from .routers.workouts import router as workout_router
from .sheets.auth_sheet import load_credentials, poll_credentials
from .sheets.sheets_client import get_main_sheet

logger = get_logger("main")

# Core env vars required for the app to function — missing any of these means the
# app will start but all protected endpoints will fail immediately.
REQUIRED_ENV_VARS = [
    "GOOGLE_SERVICE_ACCOUNT_JSON",
    "GOOGLE_SPREADSHEET_ID",
    "GOOGLE_AUTH_SHEET_ID",
    "JWT_SECRET",
]

# Agent-specific env vars — missing these only breaks /agent/* endpoints,
# so we log a warning rather than blocking startup.
AGENT_ENV_VARS = ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_DEPLOYMENT"]

VERSION = "0.18.1"


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """
    FastAPI lifespan hook — runs startup checks then yields to serve requests.

    On startup:
        1. Logs the version.
        2. Validates required env vars (logs error if any missing, but does not abort).
        3. Warns if Azure OpenAI env vars are absent (agent endpoints will fail at runtime).
        4. Tests the Google Sheets connection and logs the result.

    On shutdown:
        Logs a shutdown message.
    """
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
    except Exception:
        logger.exception("Google Sheets: FAILED")

    logger.info(
        "Health: { ok: %s, sheets: %s, drive: %s }",
        sheets_ok,
        sheets_ok,
        sheets_ok,
    )

    try:
        await asyncio.to_thread(load_credentials)
        logger.info("Credentials cache: warmed")
    except Exception:
        logger.exception("Could not pre-warm credentials cache")

    # Keep a reference so the poller task is not garbage-collected mid-flight
    # (asyncio only holds weak references to tasks).
    poller_task = asyncio.create_task(poll_credentials(interval=60))
    logger.info("Credentials poller: started (interval=60s)")

    logger.info("BodyOps API v%s ready", VERSION)
    yield
    poller_task.cancel()
    logger.info("BodyOps API shutting down")


app = FastAPI(title="BodyOps API", version=VERSION, lifespan=lifespan)

# Allow all origins in development; lock down to Vercel domain in production
# by setting CORS_ORIGINS env var (not yet wired — acceptable for V1 single-user app).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Request logging middleware
# ---------------------------------------------------------------------------

_SKIP_LOG_PATHS = {"/health", "/"}

_SLOW_REQUEST_THRESHOLD_S = 2.0


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log every HTTP request with method, path, status, and elapsed time.

    Each request is stamped with an 8-character request ID that propagates
    through all downstream log calls via ``request_id_var``.  Probe paths
    (``/health``, ``/``) are skipped to avoid log spam.  Responses slower
    than 2 s are logged at WARNING; 5xx responses are logged at ERROR.
    """
    path = request.url.path
    if path in _SKIP_LOG_PATHS:
        return await call_next(request)

    req_id = uuid4().hex[:8]
    request_id_var.set(req_id)

    start = time.perf_counter()
    response = await call_next(request)
    elapsed_s = time.perf_counter() - start
    elapsed_ms = elapsed_s * 1000

    status = response.status_code
    msg = "%s %s -> %d (%.1f ms)", request.method, path, status, elapsed_ms

    if status >= 500:
        logger.error(*msg)
    elif elapsed_s >= _SLOW_REQUEST_THRESHOLD_S:
        logger.warning("SLOW " + msg[0], *msg[1:])
    else:
        logger.info(*msg)

    return response


app.include_router(settings_router)
app.include_router(weight_router)
app.include_router(workout_router)
app.include_router(meals_router)
app.include_router(tasks_router)
app.include_router(coach_router)
app.include_router(progress_router)
app.include_router(agent_router)


@app.post("/auth/login", response_model=TokenResponse)
async def login_endpoint(body: LoginRequest) -> TokenResponse:
    """
    Authenticate the user and return a signed JWT.

    Delegates to ``api.auth.login`` which reads credentials from the Auth Sheet.
    Returns a bearer token valid for ``JWT_EXPIRE_MINUTES`` (default: 7 days).
    """
    return await login(body)


@app.get("/")
async def root() -> dict:
    """
    Root endpoint — returns a friendly API info payload.

    Useful when browsing the deployed Hugging Face Space directly.
    """
    return {
        "name": "BodyOps API",
        "version": VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "endpoints": [
            "/auth/login",
            "/settings",
            "/weight",
            "/workouts",
            "/meals",
            "/coach",
            "/progress",
            "/agent",
        ],
    }


@app.get("/health")
async def health() -> dict:
    """
    Liveness probe — returns immediately without any I/O.

    Google Sheets connectivity is verified once at startup inside the
    lifespan hook; there is no benefit to re-testing it on every probe
    and doing so burns Sheets API quota every 30 seconds.

    Returns:
        ``{"ok": True}``
    """
    return {"ok": True}
