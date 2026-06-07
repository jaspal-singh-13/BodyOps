FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# When deployed via git subtree push --prefix=api, files land at repo root.
# Copy them into api/ so the package import path (api.main) is preserved.
COPY . ./api/

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:7860/health').raise_for_status()"

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
