import pytest
from pydantic import ValidationError

from app.config import Settings

DB = {"db_host": "h.example", "db_user": "u", "db_password": "p", "db_name": "n"}


def test_database_not_configured_by_default():
    assert Settings(app_env="testing", _env_file=None).database_configured is False


def test_local_cannot_target_master():
    for env in ("development", "staging", "testing"):
        with pytest.raises(ValidationError, match="proibido usar a base 'master'"):
            Settings(app_env=env, db_target="master", _env_file=None, **DB)


def test_production_must_target_master():
    with pytest.raises(ValidationError, match="DB_TARGET deve ser 'master'"):
        Settings(app_env="production", secret_key="x" * 40, db_target="stg", _env_file=None, **DB)
    ok = Settings(
        app_env="production", secret_key="x" * 40, db_target="master", _env_file=None, **DB
    )
    assert ok.database_configured


def test_incomplete_database_config_is_rejected():
    with pytest.raises(ValidationError, match="incompleta"):
        Settings(app_env="testing", db_host="h", _env_file=None)
    with pytest.raises(ValidationError, match="DB_PASSWORD"):
        Settings(app_env="testing", db_host="h", db_user="u", db_name="n", _env_file=None)


def test_db_echo_forbidden_in_production():
    with pytest.raises(ValidationError, match="DB_ECHO"):
        Settings(
            app_env="production",
            secret_key="x" * 40,
            db_target="master",
            db_echo=True,
            _env_file=None,
        )


def test_url_handles_special_chars_and_masks_password():
    s = Settings(app_env="testing", _env_file=None, **{**DB, "db_password": "p@ss:/w#rd?%"})
    url = s.sqlalchemy_url
    assert url.password == "p@ss:/w#rd?%"  # valor intacto para o driver
    assert "p@ss" not in url.render_as_string(hide_password=True)
    assert "p@ss" not in repr(s) and "p@ss" not in str(s.db_password)
    assert url.query["charset"] == "utf8mb4"


def test_database_url_overrides_parts():
    s = Settings(app_env="testing", database_url="sqlite:///:memory:", _env_file=None)
    assert s.database_configured and s.sqlalchemy_url.get_backend_name() == "sqlite"


def test_db_target_defaults_follow_environment():
    assert Settings(app_env="development", _env_file=None).db_target == "stg"
    assert Settings(app_env="staging", _env_file=None).db_target == "stg"
    prod = Settings(app_env="production", secret_key="x" * 40, _env_file=None)
    assert prod.db_target == "master"
