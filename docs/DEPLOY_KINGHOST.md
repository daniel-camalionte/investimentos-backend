# Deploy na KingHost (sem root, WSGI, Python 3.9)

> A KingHost não tem documentação pública fácil de achar para apps Python; os passos abaixo seguem
> o padrão WSGI. Os pontos marcados com **(confirmar)** dependem do seu plano/painel.

## 1. Preparar o ambiente (via SSH, uma vez)

O virtualenv **precisa ser criado no servidor** (um venv criado no Windows não funciona no Linux).

```bash
cd ~/<pasta-da-aplicacao>            # (confirmar) onde a KingHost espera a app
python3 --version                     # esperado: 3.9.x
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Se algum pacote tentar compilar e falhar, anote o erro: usamos só pacotes com wheel pronto
(`pydantic-core`, `orjson`, `markupsafe`), então o servidor precisa de glibc ≥ 2.17.

## 2. Enviar o código (FTP)

Envie para a pasta da aplicação: `app/`, `scripts/`, `wsgi.py`, `requirements.txt`.
**Não envie:** `.venv/`, `tests/`, `.git/`, `.env`, `__pycache__/`.

## 3. Configuração (variáveis de ambiente)

Crie o arquivo `.env` **direto no servidor** (nunca no git), a partir do `.env.example`:

```env
APP_ENV=production
SECRET_KEY=<python -c "import secrets; print(secrets.token_urlsafe(48))">
CORS_ORIGINS=https://seu-frontend.com.br
LOG_LEVEL=INFO
```

Em `production` a aplicação **se recusa a iniciar** com `SECRET_KEY` fraca ou CORS `*`.
Proteja o arquivo: `chmod 600 .env`.

## 4. Validar antes de ligar o servidor web

```bash
source venv/bin/activate
python scripts/check_env.py
```

Deve terminar com `RESULTADO: tudo certo`. Cole a saída aqui se algo falhar (ela mostra versão do
Python, arquitetura, libc e quais dependências importam).

## 5. Apontar o servidor web para a aplicação **(confirmar no painel)**

- Tipo: aplicação Python/WSGI (uWSGI ou Passenger).
- Arquivo/módulo: `wsgi.py`, objeto `application`.
- Virtualenv: `<pasta>/venv`.
- Após cada deploy, reinicie a aplicação (ou `touch wsgi.py`, conforme o servidor).

## 6. Testar em produção

```bash
curl -i https://seu-dominio/api/v1/hello
# {"message":"Hello, World!","service":"investimentos-backend","version":"0.1.0"}
curl -i https://seu-dominio/health
```

## Documentação (Swagger) em produção

Por segurança, `/docs/*` fica **desligado** quando `APP_ENV=production`. Para ligar (ex.: durante os
testes iniciais), adicione `DOCS_ENABLED=true` ao `.env` do servidor e reinicie; depois desligue.

## Observações

- **Rate limit:** o armazenamento `memory://` é por processo. Com vários workers do uWSGI o limite
  efetivo multiplica. Para limites exatos, usar Redis (ou MySQL) como storage.
- **Logs:** saem em JSON no stdout/stderr, que o uWSGI grava no log da aplicação.
- **Python 3.9 está fora de suporte (EOL desde out/2025).** Vale pedir à KingHost uma versão mais
  nova; o código já é compatível com 3.9 e continua rodando em versões superiores.
