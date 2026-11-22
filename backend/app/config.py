from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/ folder, so paths work no matter where the server is started from
BASE_DIR = Path(__file__).resolve().parent.parent


DEV_JWT_SECRET = "dev-only-secret-change-me"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore")

    # "production" turns on the safety checks below (strong secrets, explicit encryption key).
    app_env: str = "development"

    database_url: str = f"sqlite:///{(BASE_DIR / 'claimsaathi.db').as_posix()}"
    jwt_secret: str = DEV_JWT_SECRET
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7
    cors_origins: str = "http://localhost:5173"

    demo_email: str = "rohit.demo@example.com"
    demo_password: str = "demo-pass-2026"

    # Uploaded documents are encrypted at rest with this Fernet key. If unset, a key is
    # generated once into <storage_dir>/.dev-key (fine locally, set it explicitly in production).
    file_encryption_key: str | None = None
    storage_dir: Path = BASE_DIR / "storage"
    max_upload_mb: int = 20
    max_pages: int = 300
    ocr_dpi: int = 200

    # An AI model reads policies, labels clauses and writes plain-language explanations.
    # ai_provider: "auto" uses Groq if GROQ_API_KEY is set, else Claude if ANTHROPIC_API_KEY is
    # set. Without any key ClaimSaathi runs in "basic mode" (rule-based, no explanations).
    ai_enabled: bool = True
    ai_provider: str = "auto"  # auto | groq | anthropic
    anthropic_api_key: str | None = None
    ai_model: str = "claude-opus-5-5"
    groq_api_key: str | None = None
    groq_model: str = "openai/gpt-oss-120b"
    groq_tokens_per_minute: int = 8000  # Groq free plan limit for gpt-oss-120b; raise on a paid plan

    # Local embedding model for clause search (downloaded once, runs on this machine)
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embeddings_enabled: bool = True
    models_dir: Path = BASE_DIR / "models"

    # The built website (npm run build). When the folder exists the API also serves the site,
    # so one server runs the whole app.
    frontend_dist: Path = BASE_DIR.parent / "frontend" / "dist"
    # Create the fictional demo account when the server starts (handy for a hosted demo).
    seed_demo: bool = False
    # Also load and read the fictional sample files for the demo account (in the background, once).
    seed_demo_documents: bool = False
    # Failed sign-ins allowed per email and address before a short lock-out.
    login_attempts: int = 10
    login_window_minutes: int = 15

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    def production_problems(self) -> list[str]:
        """Settings that must be changed before running for real users."""
        problems = []
        if self.jwt_secret == DEV_JWT_SECRET or self.jwt_secret.startswith("change-me") or len(self.jwt_secret) < 32:
            problems.append("JWT_SECRET must be a long random value (32+ characters)")
        if not self.file_encryption_key:
            problems.append("FILE_ENCRYPTION_KEY must be set (and backed up)")
        if self.seed_demo and len(self.demo_password) < 8:
            problems.append("DEMO_PASSWORD must be at least 8 characters when SEED_DEMO is on")
        return problems

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
