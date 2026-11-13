from app.api.v1 import bp
from app.version import SERVICE_NAME, __version__


@bp.get("/hello")
def hello():
    return {"message": "Hello, World!", "service": SERVICE_NAME, "version": __version__}
