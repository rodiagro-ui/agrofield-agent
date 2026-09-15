"""Browser-to-loopback diagnostic. Never enter a key: no API code is imported.

Checks headers without reading, retaining or echoing the form body. No outbound
client, inference, credential transfer or quality measurement is implemented.
"""
from __future__ import annotations

import argparse
import html
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import secrets
import time
from typing import Mapping

ORIGIN = "http://127.0.0.1:18092"


def inspect_headers(path: str, headers: Mapping[str, str], route: str) -> dict:
    checks = {
        "path_matches": path == route,
        "host_matches": headers.get("Host") == "127.0.0.1:18092",
        "origin_present": "Origin" in headers,
        "origin_matches": headers.get("Origin") == ORIGIN,
        "origin_is_null": headers.get("Origin") == "null",
        "content_type_matches": headers.get("Content-Type", "").split(";")[0]
        == "application/x-www-form-urlencoded",
    }
    return {
        "scope": "loopback_browser_header_diagnostic_no_credentials",
        "external_requests": 0,
        "api_execution_available": False,
        **checks,
        "guard_would_accept": all(checks[key] for key in (
            "path_matches", "host_matches", "origin_matches", "content_type_matches"
        )),
        "body_read": False,
    }


def serve(referrer_policy: str = "same-origin") -> None:
    if referrer_policy not in {"same-origin", "no-referrer"}:
        raise ValueError("Unsupported diagnostic policy")
    route = "/" + secrets.token_urlsafe(24)
    state = {"done": False}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, code, content):
            body = content.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Referrer-Policy", referrer_policy)
            self.send_header("Content-Security-Policy", "default-src 'none'; form-action 'self'; frame-ancestors 'none'")
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def do_GET(self):
            if self.path != route or self.headers.get("Host") != "127.0.0.1:18092":
                return self.reply(404, "Unavailable")
            self.reply(200, '<title>Diagnóstico local sin credenciales</title><h1>Sin conexión a Nebius</h1><p>Solo datos ficticios; no ingresar claves.</p><form method="post" autocomplete="off"><label>Dato ficticio<input name="dummy" value="synthetic-only"></label><button>Comprobar formulario local</button></form>')

        def do_POST(self):
            # Diagnostic only: never read the body, even for a valid origin.
            result = inspect_headers(self.path, self.headers, route)
            result["referrer_policy"] = referrer_policy
            state["done"] = True
            serialized = json.dumps(result, indent=2)
            print(serialized, flush=True)
            self.reply(200 if result["guard_would_accept"] else 403,
                       '<title>Diagnóstico terminado</title><pre>' + html.escape(serialized) + '</pre>')

    with HTTPServer(("127.0.0.1", 18092), Handler) as server:
        server.timeout = 1
        deadline = time.monotonic() + 180
        print(json.dumps({"url": ORIGIN + route, "api_execution_available": False}), flush=True)
        while not state["done"] and time.monotonic() < deadline:
            server.handle_request()
    print("DIAGNOSTIC_SERVER_CLOSED", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--referrer-policy", choices=("same-origin", "no-referrer"), default="same-origin")
    serve(parser.parse_args().referrer_policy)


if __name__ == "__main__":
    main()
