from typing import Optional

from flask import Flask

from app.api import register_blueprints
from app.config import Settings, get_settings
from app.core.errors import register_error_handlers
from app.core.http import register_http_hooks
from app.core.logging import configure_logging
from app.extensions import build_limiter, cors


def create_app(settings: Optional[Settings] = None) -> Flask:
    """Application factory: cria e configura a aplicação Flask."""
    settings = settings or get_settings()
    configure_logging(settings.log_level)

    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=settings.secret_key,
        MAX_CONTENT_LENGTH=settings.max_content_length,
        TESTING=settings.is_testing,
        JSON_SORT_KEYS=False,
    )
    app.extensions["settings"] = settings

    register_http_hooks(app, is_production=settings.is_production)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": settings.cors_origin_list}},
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
        max_age=600,
    )
    limiter = build_limiter(settings)
    limiter.init_app(app)
    app.extensions["limiter"] = limiter
    register_error_handlers(app)
    register_blueprints(app)
    limiter.exempt(app.blueprints["health"])  # monitoramento não consome cota
    return app
