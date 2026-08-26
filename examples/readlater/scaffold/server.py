"""Deliberately incomplete fictional starter: static files and health only."""

import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

WEB = Path(__file__).parent / "web"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    handler = lambda *a, **kw: SimpleHTTPRequestHandler(*a, directory=str(WEB), **kw)
    ThreadingHTTPServer(("127.0.0.1", args.port), handler).serve_forever()
