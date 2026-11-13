"""Verificações de saúde (monitoramento). Não expõem informações internas."""

from flask import Blueprint

from app.version import SERVICE_NAME, __version__

bp = Blueprint("health", __name__)


@bp.get("/health")
def liveness():
    return {"status": "ok", "service": SERVICE_NAME, "version": __version__}
