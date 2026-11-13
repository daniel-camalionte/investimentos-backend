"""Configuração tipada e validada a partir de variáveis de ambiente (.env em desenvolvimento)."""

from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL, make_url

# .env na raiz do projeto, independente do diretório de trabalho do servidor WSGI
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
_INSECURE_KEY_MARKER = "troque-esta-chave"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILE, env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(
        default="development", pattern="^(development|staging|production|testing)$"
    )
    secret_key: str = f"{_INSECURE_KEY_MARKER}-em-desenvolvimento-somente"
    cors_origins: str = "http://localhost:3000"
    log_level: str = "INFO"
    rate_limit_default: str = "120 per minute"
    rate_limit_storage_uri: str = "memory://"
    max_content_length: int = 1_048_576
    # Documentação Swagger: padrão = ligada fora de produção. Defina DOCS_ENABLED para forçar.
    docs_enabled: Optional[bool] = None
    # Prefixo público da API: https://dominio/<prefixo>/v1/...
    # Produção: a hospedagem monta a app nele (KingHost: nome da aplicação).
    # Local: o wsgi.py emula a montagem. Também alimenta o "Try it out" do Swagger.
    # Vazio = app na raiz do domínio.
    public_base_path: str = "/api"

    # --- Banco de dados (MySQL/MariaDB) ---------------------------------------------------------
    # Qual base esta instância usa. Padrão derivado do ambiente: produção => "master"; qualquer
    # outro => "stg". Declarar o valor errado para o ambiente é erro (trava de segurança).
    db_target: Optional[Literal["stg", "master"]] = None
    db_host: Optional[str] = None
    db_port: int = 3306
    db_user: Optional[str] = None
    db_password: Optional[SecretStr] = None
    db_name: Optional[str] = None
    # Sobrescreve as partes acima (ex.: sqlite:///:memory: nos testes).
    database_url: Optional[str] = None
    # Pool conservador: hospedagem compartilhada limita conexões simultâneas por usuário.
    db_pool_size: int = Field(default=3, ge=1, le=20)
    db_max_overflow: int = Field(default=2, ge=0, le=20)
    db_pool_recycle: int = Field(default=280, ge=30)  # segundos; abaixo do wait_timeout do servidor
    db_connect_timeout: int = Field(default=10, ge=1, le=60)
    db_echo: bool = False  # loga o SQL (só para depuração local; nunca em produção)

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def openapi_base_path(self) -> str:
        path = self.public_base_path.strip().strip("/")
        return f"/{path}" if path else ""

    @property
    def docs_on(self) -> bool:
        return self.docs_enabled if self.docs_enabled is not None else not self.is_production

    @property
    def is_testing(self) -> bool:
        return self.app_env == "testing"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def database_configured(self) -> bool:
        return bool(self.database_url or (self.db_host and self.db_user and self.db_name))

    @property
    def sqlalchemy_url(self) -> URL:
        """URL do SQLAlchemy. Montada por objeto (sem interpolar string): senhas com caracteres
        especiais funcionam e nunca aparecem em repr/log (a senha é mascarada)."""
        if self.database_url:
            return make_url(self.database_url)
        return URL.create(
            "mysql+pymysql",
            username=self.db_user,
            password=self.db_password.get_secret_value() if self.db_password else None,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            query={"charset": "utf8mb4"},  # o banco usa latin1 por padrão
        )

    @model_validator(mode="after")
    def _enforce_safety(self) -> "Settings":
        if self.is_production:
            if len(self.secret_key) < 32 or _INSECURE_KEY_MARKER in self.secret_key:
                raise ValueError(
                    "SECRET_KEY inválida para produção (mín. 32 caracteres, aleatória)."
                )
            if "*" in self.cors_origin_list:
                raise ValueError("CORS_ORIGINS não pode conter '*' em produção.")
            if self.db_echo:
                raise ValueError("DB_ECHO não pode ser ligado em produção (vazaria dados no log).")

        # Trava contra apontar o ambiente errado para a base errada.
        if self.db_target is None:
            self.db_target = "master" if self.is_production else "stg"
        if self.is_production and self.db_target != "master":
            raise ValueError("Em produção DB_TARGET deve ser 'master'.")
        if not self.is_production and self.db_target == "master":
            raise ValueError(
                "Fora de produção (local/stg) é proibido usar a base 'master': "
                "defina DB_TARGET=stg."
            )

        # Partes do banco: ou nenhuma, ou todas as obrigatórias (evita config pela metade).
        parts = [self.db_host, self.db_user, self.db_name]
        if any(parts) and not all(parts):
            raise ValueError("Configuração de banco incompleta: defina DB_HOST, DB_USER e DB_NAME.")
        if all(parts) and self.db_password is None:
            raise ValueError("DB_PASSWORD é obrigatório quando o banco está configurado.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
