"""Diagnóstico do banco (somente leitura). Usa as mesmas Settings da aplicação (DB_* no .env).

    python scripts/check_db.py

Mostra a base alvo (stg/master), versão do servidor, charset efetivo da conexão e nº de tabelas.
Nunca imprime a senha.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.db.engine import create_db_engine  # noqa: E402


def main() -> int:
    settings = get_settings()
    url = settings.sqlalchemy_url
    print(f"ambiente : {settings.app_env}")
    print(f"alvo     : {settings.db_target}")
    if not settings.database_configured:
        print("ERRO: banco não configurado (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME).")
        return 1
    print(f"destino  : {url.render_as_string(hide_password=True)}")

    engine = create_db_engine(settings)
    started = time.perf_counter()
    try:
        with engine.connect() as conn:
            version, db, charset, collation = conn.execute(
                text(
                    "SELECT VERSION(), DATABASE(), "
                    "@@character_set_connection, @@collation_connection"
                )
            ).one()
            tables = conn.execute(
                text(
                    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE()"
                )
            ).scalar()
    except Exception as exc:  # noqa: BLE001 - diagnóstico
        msg = str(exc)
        if settings.db_password:
            msg = msg.replace(settings.db_password.get_secret_value(), "***")
        print(f"FALHA    : {type(exc).__name__}: {msg[:300]}")
        return 1
    ms = (time.perf_counter() - started) * 1000
    print(f"servidor : {version}")
    print(f"database : {db}")
    print(f"charset  : {charset} / {collation}")
    print(f"tabelas  : {tables}")
    print(f"latência : {ms:.0f} ms (conexão + 2 consultas)")
    print("RESULTADO: conexão OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
