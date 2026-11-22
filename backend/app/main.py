import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import get_settings
from .db import SessionLocal, init_db
from .routers import auth, chat, claims, compare, complaints, documents, policies

log = logging.getLogger("claimsaathi")
settings = get_settings()


@asynccontextmanager
async def lifespan(app_: FastAPI):
    if settings.is_production and (problems := settings.production_problems()):
        raise RuntimeError("Refusing to start in production: " + "; ".join(problems))
    init_db()
    if settings.seed_demo:
        from .seed import seed

        with SessionLocal() as db:
            demo_id = seed(db).id
        if settings.seed_demo_documents:
            import threading

            from .seed import load_sample_documents

            # Skips files already loaded, so a restart doesn't read them again.
            threading.Thread(target=load_sample_documents, args=(demo_id, SessionLocal), name="seed-documents", daemon=True).start()
    from .db import get_session_factory
    from .recovery import resume_interrupted

    # Reads and checks a restart cut off would otherwise show "Reading…" for ever. Uses the same
    # session factory as the routes, so tests (which override it) never touch the real database.
    factory = app_.dependency_overrides.get(get_session_factory, get_session_factory)()
    resume_interrupted(factory)
    yield


app = FastAPI(
    title="ClaimSaathi API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None,
    openapi_url=None if settings.is_production else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    if settings.is_production:
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response


app.include_router(auth.router)
app.include_router(policies.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(compare.router)
app.include_router(claims.router)
app.include_router(complaints.router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# ---------- the website itself (after `npm run build`), so one server runs everything ----------

def serve_site(target: FastAPI, dist: Path) -> None:
    root = dist.resolve()
    index = root / "index.html"

    @target.get("/{path:path}", include_in_schema=False)
    def site(path: str) -> FileResponse:
        if path.startswith("api/") or path == "api":
            raise HTTPException(404, "Not Found")
        f = (root / path).resolve()
        if path and f.is_file() and root in f.parents:
            # Vite puts a content hash in asset names, so they can be cached for good.
            cache = "public, max-age=31536000, immutable" if path.startswith("assets/") else "public, max-age=3600"
            return FileResponse(f, headers={"Cache-Control": cache})
        return FileResponse(index, headers={"Cache-Control": "no-cache"})  # app routes like /policy


if (settings.frontend_dist / "index.html").exists():
    serve_site(app, settings.frontend_dist)
else:
    log.info("No built website at %s: serving the API only (use `npm run dev` for the site).", settings.frontend_dist)
