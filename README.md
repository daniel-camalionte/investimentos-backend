# investimentos-backend

API da plataforma de consultoria financeira (carteira, análise de ações, sugestões e day trade).

**Stack:** Python 3.9 · Flask (WSGI) · Pydantic · orjson · Flask-Limiter · (MySQL + SQLAlchemy nas próximas etapas)

## Rodando localmente

```bash
python -m venv .venv
.venv\Scripts\activate            # Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
copy .env.example .env            # Linux: cp .env.example .env
python -m flask --app wsgi run -p 5055
```

```bash
curl http://localhost:5055/api/v1/hello
# {"message":"Hello, World!","service":"investimentos-backend","version":"0.1.0"}
```

## Qualidade

```bash
python -m pytest
python -m ruff check . && python -m ruff format --check .
```

## Documentação

- [Deploy na KingHost](docs/DEPLOY_KINGHOST.md)
- [Arquitetura, segurança e evolução com agentes](docs/ARCHITECTURE.md)
- [Convenções para agentes de código](CLAUDE.md)

## Rotas

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/v1/hello` | Hello world |
| GET | `/health` | Verificação de saúde (isenta de rate limit) |
