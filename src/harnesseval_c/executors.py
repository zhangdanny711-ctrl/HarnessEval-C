"""Deterministic evidence collectors for frozen Skill configurations."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Callable

from .runtime import http_request


BrowserStepRunner = Callable[[dict[str, Any]], dict[str, Any]]


def execute_api_contracts(origin: str, config: dict[str, Any],
                          default_headers: dict[str, str] | None = None) -> dict[str, Any]:
    responses = {}
    for contract in config.get("contracts") or []:
        responses[contract["id"]] = http_request(origin, {
            "method": contract.get("method", "GET"), "path": contract["path"],
            "body": contract.get("request"), "headers": contract.get("headers", {}),
            "use_default_headers": contract.get("use_default_headers", True)}, default_headers)
    return {"responses": responses}


def execute_runtime_probes(origin: str, config: dict[str, Any],
                           default_headers: dict[str, str] | None = None) -> list[dict[str, Any]]:
    results = []
    for probe in config.get("probes") or []:
        response = http_request(origin, probe, default_headers)
        passed = response.get("status") == int((probe.get("expect") or {}).get("http_status", 200))
        results.append({"id": probe["id"], "passed": passed, "response": response})
    return results


def execute_browser_journeys(config: dict[str, Any], run_step: BrowserStepRunner) -> dict[str, Any]:
    """Execute frozen steps through an injected Playwright/Selenium adapter."""
    journeys = []
    for journey in config.get("journeys") or []:
        steps = []
        for frozen_step in journey.get("steps") or []:
            observed = run_step(dict(frozen_step))
            steps.append({**frozen_step, "passed": observed.get("passed") is True,
                          "detail": observed.get("detail")})
        journeys.append({"journey_id": journey["journey_id"], "steps": steps})
    return {"journeys": journeys}


def inspect_protected_anchors(workspace: Path, config: dict[str, Any]) -> list[dict[str, Any]]:
    results = []
    for anchor in config.get("protected_anchors") or []:
        path = workspace / anchor["path"]
        passed = path.is_file()
        if passed and "contains" in anchor:
            passed = anchor["contains"] in path.read_text(encoding="utf-8")
        if passed and "sha256" in anchor:
            passed = hashlib.sha256(path.read_bytes()).hexdigest() == anchor["sha256"]
        results.append({"id": anchor["id"], "path": anchor["path"], "passed": passed})
    return results

