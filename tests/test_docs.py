from app import create_app
from app.config import Settings


def test_openapi_spec_describes_routes(client):
    spec = client.get("/docs/openapi.json").get_json()
    assert spec["info"]["title"] == "Investimentos API"
    assert "/api/v1/hello" in spec["paths"]
    assert "/health" in spec["paths"]
    assert "HelloResponse" in spec["components"]["schemas"]


def test_swagger_ui_is_served(client):
    resp = client.get("/docs/swagger")
    assert resp.status_code == 200
    assert "text/html" in resp.content_type
    csp = resp.headers["Content-Security-Policy"]
    assert "script-src 'self'" in csp and "http" not in csp  # sem CDNs externos


def test_swagger_assets_are_local(client):
    html = client.get("/docs/swagger").get_data(as_text=True)
    assert "https://" not in html and "//cdn" not in html


def test_api_csp_stays_strict(client):
    csp = client.get("/api/v1/hello").headers["Content-Security-Policy"]
    assert csp == "default-src 'none'; frame-ancestors 'none'"


def test_docs_disabled_by_default_in_production():
    settings = Settings(app_env="production", secret_key="x" * 40, _env_file=None)
    client = create_app(settings).test_client()
    assert client.get("/docs/swagger").status_code == 404
    assert client.get("/docs/openapi.json").status_code == 404
    assert client.get("/api/v1/hello").status_code == 200


def test_docs_can_be_enabled_in_production():
    settings = Settings(
        app_env="production", secret_key="x" * 40, docs_enabled=True, _env_file=None
    )
    assert create_app(settings).test_client().get("/docs/openapi.json").status_code == 200
