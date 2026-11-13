from flask import Flask

from app.api import health
from app.api.v1 import bp as v1_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(health.bp)
    app.register_blueprint(v1_bp, url_prefix="/api/v1")
