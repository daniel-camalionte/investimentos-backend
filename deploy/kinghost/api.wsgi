# -*- coding: utf-8 -*-
# PASSO 2 (definitivo): carrega a API Flask a partir do virtualenv.
# Copiar para /home/investimentos/apps_wsgi/api.wsgi (ajuste BASE se o caminho for outro).
import os
import site
import sys

BASE = "/home/investimentos/apps_wsgi"
APP_DIR = os.path.join(BASE, "api")  # onde ficam app/, scripts/, .env
VENV = os.path.join(BASE, "venv")
SITE_PACKAGES = os.path.join(
    VENV, "lib", "python%d.%d" % sys.version_info[:2], "site-packages"
)

# O venv precisa vir ANTES dos pacotes do sistema (/usr/local/lib/...), que no servidor têm
# versões antigas (ex.: typing_extensions) e quebrariam o pydantic. `site.addsitedir` só
# acrescenta ao FIM do sys.path, então reordenamos.
_before = list(sys.path)
site.addsitedir(SITE_PACKAGES)
_added = [p for p in sys.path if p not in _before]
sys.path[:] = _added + [p for p in sys.path if p not in _added]
sys.path.insert(0, APP_DIR)
os.chdir(APP_DIR)

# se o mod_wsgi/sistema já importou alguma versão do sistema, descarta para reimportar do venv
for _name in ("typing_extensions",):
    _mod = sys.modules.get(_name)
    if _mod is not None and not (getattr(_mod, "__file__", "") or "").startswith(VENV):
        del sys.modules[_name]

from app import create_app  # noqa: E402

application = create_app()
