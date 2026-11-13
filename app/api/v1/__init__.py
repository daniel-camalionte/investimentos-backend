from flask import Blueprint

bp = Blueprint("v1", __name__)

from app.api.v1 import hello  # noqa: E402,F401  (registra as rotas no blueprint)
