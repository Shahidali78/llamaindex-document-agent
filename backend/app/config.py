"""Application configuration loaded from environment variables.

All settings can be overridden via a local ``.env`` file (see ``.env.example``)
or real environment variables. No secrets are hardcoded here.
"""

from __future__ import annotations

from functools import cached_property
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/ directory (two levels up from this file: app/config.py -> app -> backend)
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Strongly typed application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        protected_namespaces=("settings_",),
    )

    # --- General ---
    app_name: str = "LlamaIndex AI Document Intelligence Platform"
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "*"

    # --- OpenAI ---
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    # --- Authentication ---
    # When enabled, all data/AI endpoints require a valid 'X-API-Key' header.
    auth_enabled: bool = True
    # Optional comma-separated static keys (instant access without minting).
    api_keys: str = ""
    # Admin token that gates the /auth key-management API. Empty = disabled.
    admin_api_token: str = ""

    # --- Indexing / retrieval ---
    chunk_size: int = 1024
    chunk_overlap: int = 128
    similarity_top_k: int = 4
    max_extract_chars: int = 24000
    max_upload_mb: int = 25

    # --- Storage ---
    data_dir: Path = BASE_DIR / "data"

    @cached_property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    @cached_property
    def index_storage_dir(self) -> Path:
        return self.data_dir / "index_storage"

    @cached_property
    def db_path(self) -> Path:
        return self.data_dir / "app.db"

    @cached_property
    def database_url(self) -> str:
        return f"sqlite:///{self.db_path.as_posix()}"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def api_key_list(self) -> list[str]:
        return [k.strip() for k in self.api_keys.split(",") if k.strip()]

    def ensure_dirs(self) -> None:
        """Create all storage directories if they do not yet exist."""
        for path in (self.data_dir, self.uploads_dir, self.index_storage_dir):
            path.mkdir(parents=True, exist_ok=True)


settings = Settings()
