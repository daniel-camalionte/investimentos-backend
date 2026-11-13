"""Verificações de saúde (monitoramento). Não expõem informações internas."""

import time

from flask import current_app
from flask_openapi3 import APIBlueprint, Tag
from sqlalchemy import text

from app.db import get_engine
from app.schemas.system import HealthResponse, ReadinessResponse
from app.version import SERVICE_NAME, __version__

bp = APIBlueprint("health", __name__, abp_tags=[Tag(name="Sistema")])

_CACHE_TTL = 5.0  # s — evita que monitoramento/abuso martele o banco


@bp.get("/health", summary="Liveness", responses={200: HealthResponse})
def liveness():
    """Indica que o processo está de pé. Isento de rate limit."""
    return HealthResponse(status="ok", service=SERVICE_NAME, version=__version__).model_dump()


def _database_state() -> str:
    engine = get_engine()
    if engine is None:
        return "not_configured"
    cache = current_app.extensions.setdefault("health_cache", {"at": 0.0, "value": None})
    now = time.monotonic()
    if cache["value"] is not None and now - cache["at"] < _CACHE_TTL:
        return cache["value"]
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        state = "ok"
    except Exception:  # noqa: BLE001 - qualquer falha = indisponível; detalhe só no log
        current_app.logger.exception("database_readiness_failed")
        state = "unavailable"
    cache.update(at=now, value=state)
    return state


@bp.get(
    "/health/ready",
    summary="Readiness (inclui banco)",
    responses={200: ReadinessResponse, 503: ReadinessResponse},
)
def readiness():
    """Verifica as dependências (banco). 503 se indisponível. Sem detalhes internos."""
    database = _database_state()
    healthy = database in ("ok", "not_configured")
    body = ReadinessResponse(
        status="ok" if healthy else "degraded", database=database, service=SERVICE_NAME
    ).model_dump()
    resp = current_app.json.response(body)
    resp.status_code = 200 if healthy else 503
    return resp
