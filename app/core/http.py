"""Comportamentos transversais de HTTP: request id, cabeçalhos de segurança e JSON (orjson)."""

import re
import time
import uuid

import orjson
from flask import Flask, Response, g, request
from flask.json.provider import JSONProvider

_REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9._-]{8,64}$")


class OrjsonProvider(JSONProvider):
    """Serialização JSON com orjson (bem mais rápida que o json da stdlib)."""

    def dumps(self, obj, **kwargs) -> str:
        return orjson.dumps(obj, option=orjson.OPT_NON_STR_KEYS).decode()

    def loads(self, s, **kwargs):
        return orjson.loads(s)

    def response(self, *args, **kwargs) -> Response:
        obj = self._prepare_response_obj(args, kwargs)
        return Response(
            orjson.dumps(obj, option=orjson.OPT_NON_STR_KEYS), mimetype="application/json"
        )


def register_http_hooks(app: Flask, *, is_production: bool) -> None:
    app.json = OrjsonProvider(app)

    @app.before_request
    def _start():
        incoming = request.headers.get("X-Request-ID", "")
        # só aceitamos IDs bem formados (evita log injection); senão geramos um novo
        g.request_id = incoming if _REQUEST_ID_RE.match(incoming) else uuid.uuid4().hex
        g.started_at = time.perf_counter()

    @app.after_request
    def _finish(response: Response) -> Response:
        response.headers["X-Request-ID"] = g.get("request_id", "")
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
        response.headers.setdefault("Cache-Control", "no-store")
        if is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        started = g.get("started_at")
        if started is not None:
            app.logger.info(
                "request",
                extra={
                    "method": request.method,
                    "path": request.path,
                    "status": response.status_code,
                    "ms": round((time.perf_counter() - started) * 1000, 2),
                },
            )
        return response
