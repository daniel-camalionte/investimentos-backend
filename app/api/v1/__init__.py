from flask_openapi3 import APIBlueprint, Tag

bp = APIBlueprint("v1", __name__, url_prefix="/api/v1", abp_tags=[Tag(name="Sistema")])

from app.api.v1 import hello  # noqa: E402,F401  (registra as rotas no blueprint)
