"""Configuração tipada e validada a partir de variáveis de ambiente (.env em desenvolvimento)."""

from functools import lru_cache
from typing import Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_KEY_MARKER = "troque-esta-chave"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="development", pattern="^(development|production|testing)$")
    secret_key: str = f"{_INSECURE_KEY_MARKER}-em-desenvolvimento-somente"
    cors_origins: str = "http://localhost:3000"
    log_level: str = "INFO"
    rate_limit_default: str = "120 per minute"
    rate_limit_storage_uri: str = "memory://"
    max_content_length: int = 1_048_576
    database_url: Optional[str] = None

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_testing(self) -> bool:
        return self.app_env == "testing"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @model_validator(mode="after")
    def _enforce_production_safety(self) -> "Settings":
        if self.is_production:
            if len(self.secret_key) < 32 or _INSECURE_KEY_MARKER in self.secret_key:
                raise ValueError(
                    "SECRET_KEY inválida para produção (mín. 32 caracteres, aleatória)."
                )
            if "*" in self.cors_origin_list:
                raise ValueError("CORS_ORIGINS não pode conter '*' em produção.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
