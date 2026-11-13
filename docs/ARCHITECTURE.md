# Arquitetura

## Restrições que moldam as decisões

| Restrição | Consequência |
|---|---|
| KingHost, sem root, Python 3.9 | Só pacotes com wheel; sem serviços de sistema; código compatível com 3.9 |
| Servidor WSGI (uWSGI/Passenger) | Flask (WSGI nativo) em vez de FastAPI/ASGI; sem WebSocket nativo |
| MySQL/MariaDB | SQLAlchemy 2 + PyMySQL (puro Python) + Alembic |
| Performance e segurança | orjson, limites de taxa, cabeçalhos de segurança, validação estrita de config |
| Evolução com agentes e skills | Camada `agents/` isolada do HTTP (ver abaixo) |

> Tempo real (cotações/day trade) via WebSocket não roda em WSGI. Alternativas quando chegar a
> hora: polling/SSE com cache curto, ou um serviço separado só para streaming.

## Estrutura

```
app/
  __init__.py        create_app() — application factory
  config.py          Settings (pydantic-settings), validação rígida em produção
  extensions.py      CORS e rate limiter
  version.py
  core/
    http.py          request id, cabeçalhos de segurança, JSON (orjson), log de requisição
    errors.py        AppError + handlers globais (nunca vazam detalhes internos)
    logging.py       logs JSON estruturados com request_id
  api/
    health.py        /health (liveness) e /health/ready (banco)
  db/                engine (pool), sessão por requisição, Base declarativa
  schemas/           modelos Pydantic (entrada/saída) — também geram o OpenAPI/Swagger
    v1/              rotas versionadas (internas /v1/..., públicas /api/v1/...)
wsgi.py              entrada WSGI (objeto `application`)
scripts/check_env.py diagnóstico do servidor
tests/               pytest
```

### Camadas planejadas (próximas etapas)

```
api/v1/<recurso>.py   HTTP: valida entrada (Pydantic), chama o serviço, serializa
services/             regras de negócio (carteira, análise, sugestões) — sem Flask
repositories/         acesso a dados (SQLAlchemy)
models/               entidades ORM
schemas/              modelos Pydantic de entrada/saída
integrations/         provedores de cotação (B3/brapi/etc.) atrás de interfaces
agents/               agentes de IA e skills (ver abaixo)
```

Regra: `services/` e `agents/` **não importam Flask**. Assim a mesma lógica serve a API, a
tarefas agendadas e aos agentes.

## Segurança (já implementado)

- Config falha na inicialização em produção com `SECRET_KEY` fraca ou CORS `*`.
- Cabeçalhos: `nosniff`, `X-Frame-Options`, CSP `default-src 'none'`, `Referrer-Policy`,
  `Permissions-Policy`, `Cache-Control: no-store`, HSTS em produção.
- CORS com lista de origens explícita, só em `/v1/*`.
- Rate limit global por IP; limite de tamanho do corpo (1 MB).
- `X-Request-ID` só é aceito se bem formado (evita log injection).
- Erros 5xx genéricos para o cliente; detalhe só no log.

### Pendente

Autenticação (JWT de curta duração + refresh, hash Argon2), RBAC, auditoria de ações
financeiras, rotação de segredos, rate limit por usuário/rota sensível, validação de entrada com
Pydantic em todas as rotas, proteção de dados pessoais (LGPD).

## Performance

- orjson para (de)serialização JSON.
- Sem estado em memória que impeça múltiplos workers.
- Próximos passos: pool de conexões SQLAlchemy ajustado ao limite do plano, cache de cotações
  (TTL curto) e índices desenhados junto com as consultas.

## Agentes e skills (evolução)

Objetivo: permitir que agentes de IA (análise de ativos, sugestões, resumo de carteira) evoluam
sem acoplar ao HTTP.

- `agents/skills/`: cada skill é uma função/classe com **contrato tipado** (entrada/saída
  Pydantic), descrição em linguagem natural e permissões explícitas (somente leitura vs. escrita).
- `agents/` orquestra: recebe a intenção, escolhe skills, registra cada chamada (auditoria).
- Skills reutilizam `services/` — nunca acessam o banco diretamente.
- Ações financeiras (ordens, alterações de carteira) exigem confirmação humana explícita.
- Saídas de recomendação carregam aviso de que **não constituem recomendação personalizada de
  investimento** (rever com assessoria jurídica/CVM antes de lançar).
- Também mantemos `CLAUDE.md` na raiz para que agentes de código sigam as convenções do projeto.
