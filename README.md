# investimentos-backend

API da plataforma de consultoria financeira (carteira, análise de ações, sugestões e day trade).

**Stack:** Python 3.9 · Flask (WSGI) · Pydantic · orjson · Flask-Limiter · (MySQL + SQLAlchemy nas próximas etapas)

## Rodando localmente

```bash
python -m venv .venv
.venv\Scripts\activate            # Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
copy .env.example .env            # Linux: cp .env.example .env
python wsgi.py                    # http://localhost:8000
```

```bash
curl http://localhost:8000/api/v1/hello
# {"message":"Hello, World!","service":"investimentos-backend","version":"0.1.0"}
```

## Rodando com Docker

```bash
docker build -t investimentos-backend-api .
docker compose up -d --no-build     # http://localhost:8000
docker compose logs -f api
docker compose down
```

O container usa Python 3.9, usuário sem privilégios, filesystem somente leitura e gunicorn (mesmo
contrato WSGI do servidor). Swagger: <http://localhost:8000/api/docs/swagger>.

## Banco de dados

- **MariaDB/MySQL** via SQLAlchemy 2 + PyMySQL; migrações com Alembic (`migrations/`).
- **Local = sempre STG; produção = Master.** O ambiente decide a base (`DB_TARGET` é derivado) e a
  aplicação **recusa iniciar** se `APP_ENV` diferente de `production` apontar para `master`.
- Credenciais só em variáveis de ambiente (`.env` local ignorado pelo git; `.env` no servidor).

```bash
python scripts/check_db.py          # testa a conexão (somente leitura, não imprime a senha)
python -m alembic revision --autogenerate -m "descricao"   # gera migração
python -m alembic upgrade head      # aplica (local => STG)
```

Saúde: `GET /api/health/ready` (200 com `database: ok`; 503 se o banco cair; sem detalhes internos).

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
| GET | `/api/health` | Verificação de saúde (isenta de rate limit) |

Todas as URLs têm o prefixo público `/api`, igual em todos os ambientes:

| Ambiente | Front | API |
|---|---|---|
| Local / stg | http://localhost:3000 | http://localhost:8000/api |
| Produção | https://www.investimentos.kinghost.net | https://www.investimentos.kinghost.net/api |

Internamente a app serve `/v1/...`; quem a monta em `/api` é a hospedagem (produção) ou o
`wsgi.py` (local).

## Documentação da API (Swagger)

Com o servidor rodando (fora de produção):

- Swagger UI: <http://localhost:8000/api/docs/swagger>
- Contrato OpenAPI: <http://localhost:8000/api/docs/openapi.json>

A documentação é gerada dos schemas Pydantic das rotas (`app/schemas/`), então nunca diverge da
validação. Os arquivos do Swagger UI são servidos localmente (sem CDN). **Em produção fica desligada
por padrão**; para habilitar, defina `DOCS_ENABLED=true`.
