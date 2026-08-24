"""Generic command/runtime primitives driven entirely by case configuration."""

from __future__ import annotations

import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def run_command(argv: list[str], cwd: Path, timeout: float = 120) -> dict[str, Any]:
    started = time.monotonic()
    try:
        completed = subprocess.run(argv, cwd=cwd, text=True, capture_output=True,
                                   timeout=timeout, check=False)
        return {"passed": completed.returncode == 0, "exit_code": completed.returncode,
                "stdout": completed.stdout[-4000:], "stderr": completed.stderr[-4000:],
                "elapsed_seconds": round(time.monotonic() - started, 6)}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"passed": False, "exit_code": None, "error_type": type(exc).__name__,
                "elapsed_seconds": round(time.monotonic() - started, 6)}


def http_request(origin: str, action: dict[str, Any], default_headers: dict[str, str] | None = None) -> dict[str, Any]:
    headers = dict(default_headers or {}) if action.get("use_default_headers", True) else {}
    headers.update(action.get("headers") or {})
    body = action.get("body")
    encoded = None if body is None else json.dumps(body).encode()
    if encoded is not None:
        headers.setdefault("Content-Type", "application/json")
    request = urllib.request.Request(origin.rstrip("/") + action["path"], data=encoded,
                                     headers=headers, method=action.get("method", "GET"))
    try:
        with urllib.request.urlopen(request, timeout=float(action.get("timeout", 10))) as response:
            raw = response.read().decode()
            return {"status": response.status, "body": json.loads(raw) if raw else None}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        return {"status": exc.code, "body": json.loads(raw) if raw else None}


def collect_build_evidence(workspace: Path, runtime_config: dict[str, Any]) -> list[dict[str, Any]]:
    results = []
    for item in runtime_config.get("build_commands") or []:
        result = run_command(list(item["argv"]), workspace / item.get("cwd", "."),
                             float(item.get("timeout", 120)))
        results.append({"name": item["name"], **result})
    return results

