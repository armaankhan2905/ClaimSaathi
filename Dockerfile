# ClaimSaathi: one container that serves the website and the API.
#
#   docker build -t claimsaathi .
#   docker run -p 8000:8000 -v claimsaathi-data:/data --env-file backend/.env.production claimsaathi
#
# Everything that must survive a restart (database, encrypted uploads, search model) lives in /data,
# so mount a persistent volume there. Run a single instance: background reading, the AI rate limit and
# the sign-in limit are kept in memory.

# ---- 1. build the website ----
FROM node:22-slim AS web
WORKDIR /web
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---- 2. the server ----
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_ENV=production \
    DATABASE_URL=sqlite:////data/claimsaathi.db \
    STORAGE_DIR=/data/storage \
    MODELS_DIR=/data/models \
    FRONTEND_DIST=/app/frontend/dist \
    PORT=8000

# libgomp1: ONNX runtime (OCR and clause search); libglib2.0-0: OpenCV used by the OCR
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install -r requirements.txt
COPY backend/app ./app
COPY samples /app/samples
COPY --from=web /web/dist /app/frontend/dist

RUN useradd --create-home --uid 10001 claimsaathi && mkdir -p /data && chown claimsaathi /data
USER claimsaathi
VOLUME /data
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\", \"8000\")}/api/health')"

# --proxy-headers: behind a hosting proxy, use the visitor's address (for the sign-in limit)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*'"]
