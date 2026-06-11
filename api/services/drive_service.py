"""
Google Drive upload service for meal photos.

Uploads a JPEG/PNG image to the configured Drive folder and returns a
permanent public URL.  The service account used for Sheets access is reused
here — it must have at least Contributor access to the target folder.

The target folder MUST live inside a Shared Drive (Team Drive).  Service
accounts have no personal storage quota and cannot upload to "My Drive".
Add the service account e-mail as a member of the Shared Drive (Content
Manager or above), then set GOOGLE_DRIVE_FOLDER_ID to a folder inside it.

Required env vars:
    GOOGLE_SERVICE_ACCOUNT_JSON  — full service account JSON as a string.
    GOOGLE_DRIVE_FOLDER_ID       — ID of a Shared Drive folder for meal images.
"""

from __future__ import annotations

import io
import json
import os
import time
from datetime import datetime, timezone

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from ..logger import get_logger

logger = get_logger("services.drive")

SCOPES = [
    "https://www.googleapis.com/auth/drive",
]

_drive_service = None


def _get_drive_service():
    """Return a cached Google Drive API v3 service client."""
    global _drive_service
    if _drive_service is None:
        creds_dict = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        _drive_service = build("drive", "v3", credentials=creds)
    return _drive_service


async def upload_meal_image(data: bytes, mime_type: str) -> str:
    """
    Upload a meal photo to Google Drive and return its public URL.

    Creates a file in the configured Drive folder, sets the permission to
    public reader so the URL is accessible without authentication, and returns
    the direct-download URL in the form ``https://drive.google.com/uc?id=…``.

    Args:
        data: Raw image bytes (JPEG or PNG).
        mime_type: MIME type of the image (e.g. ``"image/jpeg"``).

    Returns:
        Permanent public Google Drive URL string.

    Raises:
        KeyError: If ``GOOGLE_SERVICE_ACCOUNT_JSON`` or
            ``GOOGLE_DRIVE_FOLDER_ID`` are not set.
        googleapiclient.errors.HttpError: On Drive API failure.
    """
    size_kb = len(data) / 1024
    logger.info("Drive upload start size=%.1f KB mime_type=%s", size_kb, mime_type)
    t0 = time.perf_counter()

    service = _get_drive_service()
    folder_id = os.environ["GOOGLE_DRIVE_FOLDER_ID"]

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    ext = "jpg" if "jpeg" in mime_type else "png"
    filename = f"meal_{timestamp}.{ext}"

    file_metadata = {
        "name": filename,
        "parents": [folder_id],
    }
    media = MediaIoBaseUpload(io.BytesIO(data), mimetype=mime_type, resumable=False)

    # Run synchronously in a thread-pool to avoid blocking the event loop
    import asyncio
    loop = asyncio.get_event_loop()
    # supportsAllDrives=True is required for uploads into Shared Drives.
    # Service accounts have no personal Drive quota, so the target folder
    # must be inside a Shared Drive.
    file_obj = await loop.run_in_executor(
        None,
        lambda: service.files()
        .create(
            body=file_metadata,
            media_body=media,
            fields="id",
            supportsAllDrives=True,
        )
        .execute(),
    )

    file_id = file_obj["id"]

    # Grant public read permission so the URL is accessible without auth.
    permission = {"type": "anyone", "role": "reader"}
    await loop.run_in_executor(
        None,
        lambda: service.permissions()
        .create(fileId=file_id, body=permission, supportsAllDrives=True)
        .execute(),
    )

    elapsed_ms = (time.perf_counter() - t0) * 1000
    logger.info("Drive upload done file_id=%s filename=%s (%.0f ms)", file_id, filename, elapsed_ms)

    return f"https://drive.google.com/uc?id={file_id}"
