from sqlalchemy import text

from app import create_app
from app.config import Settings
from app.db import get_session


def _app(**overrides):
    return create_app(Settings(app_env="testing", _env_file=None, **overrides))


def test_readiness_without_database_is_ok_but_flagged(client):
    resp = client.get("/health/ready")
    assert resp.status_code == 200
    assert resp.get_json()["database"] == "not_configured"


def test_readiness_ok_with_database():
    resp = _app(database_url="sqlite:///:memory:").test_client().get("/health/ready")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok", "database": "ok", "service": "investimentos-backend"}


def test_readiness_503_when_database_down_and_no_leak():
    app = _app(
        db_host="127.0.0.1",
        db_port=1,
        db_user="segredo_user",
        db_password="segredo_pwd",
        db_name="segredo_db",
        db_connect_timeout=1,
    )
    resp = app.test_client().get("/health/ready")
    body = resp.get_data(as_text=True)
    assert resp.status_code == 503
    assert resp.get_json()["database"] == "unavailable"
    for secret in ("segredo_user", "segredo_pwd", "segredo_db", "127.0.0.1"):
        assert secret not in body


def test_session_is_per_request_and_closed():
    app = _app(database_url="sqlite:///:memory:")

    @app.get("/probe")
    def probe():
        s = get_session()
        assert get_session() is s  # mesma sessão dentro da requisição
        return {"value": s.execute(text("SELECT 41 + 1")).scalar()}

    assert app.test_client().get("/probe").get_json() == {"value": 42}


def test_get_session_without_database_raises_clear_error(client):
    app = client.application

    @app.get("/probe2")
    def probe2():
        get_session()

    app.config["PROPAGATE_EXCEPTIONS"] = False
    resp = client.get("/probe2")
    assert resp.status_code == 500
    assert "DB_" not in resp.get_data(as_text=True)  # erro interno não vaza para o cliente
