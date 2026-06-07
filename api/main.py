"""FastAPI application entry point."""
import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import LoginRequest, TokenResponse, login
from .routers.settings import router as settings_router
from .sheets.sheets_client import get_main_sheet

app = FastAPI(title="BodyOps API", version="0.2.0")

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
