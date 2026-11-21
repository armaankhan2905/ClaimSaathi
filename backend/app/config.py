from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/ folder, so paths work no matter where the server is started from
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = f"sqlite:///{(BASE_DIR / 'claimsaathi.db').as_posix()}"
    jwt_secret: str = "dev-only-secret-change-me"
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

    # Claude reads policies, labels clauses and writes plain-language explanations. Without a
    # key ClaimSaathi falls back to "basic mode" (rule-based extraction, no explanations).
    anthropic_api_key: str | None = None
    ai_model: str = "claude-opus-5-5"
    ai_enabled: bool = True

    # Local embedding model for clause search (downloaded once, runs on this machine)
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embeddings_enabled: bool = True

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
