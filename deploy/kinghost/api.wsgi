# -*- coding: utf-8 -*-
# PASSO 2 (definitivo): carrega a API Flask a partir do virtualenv.
# Copiar para /home/investimentos/apps_wsgi/api.wsgi (ajuste BASE se o caminho for outro).
import os
import site
import sys

BASE = "/home/investimentos/apps_wsgi"
APP_DIR = os.path.join(BASE, "api")  # onde ficam app/, scripts/, .env
VENV = os.path.join(BASE, "venv")

# bibliotecas instaladas no virtualenv
site.addsitedir(
    os.path.join(VENV, "lib", "python%d.%d" % sys.version_info[:2], "site-packages")
)
sys.path.insert(0, APP_DIR)
os.chdir(APP_DIR)

from app import create_app  # noqa: E402

application = create_app()
