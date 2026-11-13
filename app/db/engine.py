"""Criação do engine SQLAlchemy a partir das Settings."""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from app.config import Settings


def create_db_engine(settings: Settings) -> Engine:
    """Engine preguiçoso: não abre conexão até a primeira consulta (o app sobe mesmo sem banco)."""
    url = settings.sqlalchemy_url
    kwargs = {"echo": settings.db_echo, "future": True}

    if url.get_backend_name() == "sqlite":  # testes: sem pool nem timeouts de rede
        return create_engine(url, **kwargs)

    return create_engine(
        url,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_recycle=settings.db_pool_recycle,
        pool_pre_ping=True,  # descarta conexões mortas (a hospedagem derruba as ociosas)
        connect_args={"connect_timeout": settings.db_connect_timeout},
        **kwargs,
    )
