# investimentos-backend

API (Flask, WSGI) da plataforma de consultoria financeira. Hospedada na KingHost **sem root**,
**Python 3.9**, MySQL/MariaDB. Prioridades: **performance e segurança**.

## Comandos

```bash
python -m venv .venv && .venv/Scripts/activate      # Windows; use bin/activate no Linux
pip install -r requirements-dev.txt
python -m pytest                                     # testes
python -m ruff check . && python -m ruff format .    # lint + formatação
python wsgi.py                                       # servidor local em http://localhost:8000/api
python scripts/check_env.py                          # diagnóstico de ambiente
```

## Regras

- **Compatibilidade Python 3.9**: use `Optional[X]`, `list[str]`/`dict[str, X]` (ok), nada de
  `X | None`, `match`, nem `zip(strict=)`. Teste sempre com 3.9.
- **Dependências**: só pacotes com wheel pronto (sem compilar). Fixe versões em `requirements.txt`
  e valide a resolução em 3.9 antes de adicionar.
- **Camadas**: rotas em `app/api/v1/` ficam finas; regra de negócio em `services/` (sem Flask);
  dados em `repositories/`. Skills/agentes reutilizam `services/`.
- **Segurança**: valide toda entrada com Pydantic; nunca logue segredos/dados pessoais; erros 5xx
  genéricos; segredos só por variável de ambiente (`.env` nunca versionado); consultas SQL sempre
  parametrizadas.
- **Documentação**: toda rota declara `summary`, docstring e `responses={...}` com modelos Pydantic
  de `app/schemas/` (o Swagger sai deles). Swagger em `/api/docs/swagger` (off em produção). Rotas internas são `/v1/...`; o prefixo `/api`
  vem da montagem (KingHost/wsgi.py).
- **Testes**: toda rota nova vem com teste (caminho feliz + erro + autorização).
- **Commits**: mensagens em português, no imperativo, escopo claro.
