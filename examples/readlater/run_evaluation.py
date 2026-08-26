"""Run the frozen ReadLater Case and write recorded public evaluation evidence."""

from __future__ import annotations

import ast
import contextlib
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPOSITORY = ROOT.parents[1]
SUBJECT = ROOT / "subject"
sys.path.insert(0, str(REPOSITORY / "src"))

from harnesseval_c.io import atomic_write_json, directory_digest, read_json, value_digest  # noqa: E402
from harnesseval_c.planner import validate_plan  # noqa: E402
from harnesseval_c.preregistration import validate_preregistration  # noqa: E402
from harnesseval_c.report import build_evidence_tree  # noqa: E402
from harnesseval_c.runner import execute_frozen_evaluation  # noqa: E402
from harnesseval_c.runtime import http_request, run_command  # noqa: E402
from harnesseval_c.executors import execute_api_contracts, execute_runtime_probes  # noqa: E402
from harnesseval_c.skills import default_registry  # noqa: E402
from harnesseval_c.skills.api_contract import evaluate as evaluate_api  # noqa: E402
from harnesseval_c.skills.browser_flow import evaluate as evaluate_browser  # noqa: E402
from harnesseval_c.validation import validate_evaluation  # noqa: E402
from showcase_config import GENERATOR_CONFIG_DIGEST, MODEL_ID  # noqa: E402


def allocate_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_for_health(origin: str, process: subprocess.Popen) -> dict:
    for _ in range(80):
        if process.poll() is not None:
            raise RuntimeError("subject process exited before health check")
        try:
            response = http_request(origin, {"method": "GET", "path": "/health", "timeout": 1})
            if response.get("status") == 200:
                body = response.get("body") or {}
                return {"name": "http_health", "passed": body.get("code") == "OK",
                        "response": response}
        except OSError:
            pass
        time.sleep(0.05)
    raise RuntimeError("subject did not become healthy")


@contextlib.contextmanager
def subject_server():
    port = allocate_port()
    process = subprocess.Popen(
        [sys.executable, "server.py", "--port", str(port)],
        cwd=SUBJECT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    origin = f"http://127.0.0.1:{port}"
    try:
        health = wait_for_health(origin, process)
        yield origin, health
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def build_evidence() -> list[dict]:
    python_check = run_command([
        sys.executable, "-c",
        "from pathlib import Path; compile(Path('server.py').read_text(), 'server.py', 'exec')",
    ], SUBJECT)
    node = shutil.which("node")
    if node is None:
        javascript_check = {"passed": False, "exit_code": None, "error_type": "NodeNotFound"}
    else:
        javascript_check = run_command([node, "--check", "web/app.js"], SUBJECT)
    return [
        {"name": "python_compile", **python_check},
        {"name": "javascript_syntax", **javascript_check},
    ]


def browser_evidence(origin: str) -> dict:
    node = shutil.which("node")
    if node is None:
        raise RuntimeError("Node.js is required for the frozen browser journey")
    command = [node, "browser_check.cjs", origin, "frozen/preregistration.json"]
    completed = subprocess.run(
        command, cwd=ROOT, text=True, capture_output=True, timeout=90, check=False,
        env=dict(os.environ),
    )
    if completed.returncode != 0:
        raise RuntimeError(f"browser automation failed with exit code {completed.returncode}")
    value = json.loads(completed.stdout)
    value["automation"] = {
        "engine": "Playwright",
        "browser_channel": os.environ.get("PLAYWRIGHT_CHANNEL", "chrome"),
        "headless": True,
        "exit_code": completed.returncode,
    }
    return value


def diff_hygiene_evidence(builds: list[dict]) -> dict:
    python_source = (SUBJECT / "server.py").read_text(encoding="utf-8")
    javascript_source = (SUBJECT / "web" / "app.js").read_text(encoding="utf-8")
    imports = set()
    for node in ast.walk(ast.parse(python_source)):
        if isinstance(node, ast.Import):
            imports.update(item.name.split(".")[0] for item in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    allowed = {
        "__future__", "argparse", "datetime", "http", "json", "pathlib",
        "threading", "urllib", "uuid",
    }
    combined = f"{python_source}\n{javascript_source}".lower()
    return {"checks": [
        {"id": "python_syntax", "passed": builds[0]["passed"] is True},
        {"id": "javascript_syntax", "passed": builds[1]["passed"] is True},
        {"id": "no_placeholder_markers",
         "passed": not any(marker in combined for marker in ("todo", "fixme", "not implemented"))},
        {"id": "no_dynamic_code_execution",
         "passed": "eval(" not in combined and "exec(" not in combined},
        {"id": "standard_library_backend", "passed": imports <= allowed,
         "observed_import_roots": sorted(imports)},
    ]}


def requirement_evidence(api_result: dict, browser_result: dict) -> dict:
    contracts = {
        item["id"]: item["passed"] is True
        for item in api_result["evidence"]["contracts"]
    }
    journey_passed = all(
        item.get("passed") is True for item in browser_result["evidence"]["journeys"]
    )
    bindings = {
        "R1": (contracts.get("A1_SAVE", False), ["A1_SAVE"]),
        "R2": (contracts.get("A2_LIST", False), ["A2_LIST"]),
        "R3": (contracts.get("A3_MARK_READ", False), ["A3_MARK_READ"]),
        "R4": (contracts.get("A4_REJECT_BLANK", False), ["A4_REJECT_BLANK"]),
        "R5": (journey_passed, ["J1"]),
    }
    return {"requirements": {
        req_id: {"passed": passed, "detectors": detectors}
        for req_id, (passed, detectors) in bindings.items()
    }}


def render_summary(score: dict, tree: dict, subject_digest: str) -> str:
    lines = [
        "# Recorded evaluation — ReadLater",
        "",
        "This is a real local execution against the included fictional subject, not illustrative data.",
        "No remote LLM judge or credential was used.",
        "",
        "## Scores",
        "",
        "| Skill | Role | Status | Score |",
        "|---|---|---:|---:|",
    ]
    for item in score["skill_results"]:
        lines.append(f"| `{item['skill_id']}` | {item['role']} | {item['status']} | {item['score']:.6f} |")
    lines += [
        "",
        f"- **Core:** {score['core_score']:.6f}",
        f"- **Observation:** {score['observation_score']:.6f}",
        f"- **Final:** {score['final_score']:.6f}",
        f"- **Validation:** {score['evaluation_status']}",
        "",
        "## Recorded evidence",
        "",
        "- Two syntax/build commands executed locally.",
        "- Three independent subject processes served Runtime, API, and Browser checks.",
        "- Four stateful runtime probes and four API contracts executed over HTTP.",
        "- One six-step browser journey executed in headless Chrome through Playwright.",
        "- Five deterministic diff-hygiene checks supplied the Observation score.",
        f"- Subject directory digest: `{subject_digest}`",
        f"- Evidence Tree digest: `{tree['evidence_digest']}`",
        "",
        "See [`evidence_tree.json`](evidence_tree.json) for step-level evidence.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    case = read_json(ROOT / "case.json")
    spec_text = (ROOT / "spec" / "readlater.md").read_text(encoding="utf-8")
    plan = read_json(ROOT / "frozen" / "plan.json")
    preregistration = read_json(ROOT / "frozen" / "preregistration.json")
    registry = default_registry()
    validate_plan(plan, case, registry, MODEL_ID)
    validate_preregistration(
        preregistration, case, spec_text, GENERATOR_CONFIG_DIGEST
    )

    builds = build_evidence()
    with subject_server() as (origin, health):
        runtime = {
            "builds": builds,
            "health": [health],
            "probes": execute_runtime_probes(
                origin, preregistration["components"]["runtime_behavior"]
            ),
        }
    with subject_server() as (origin, _health):
        api = execute_api_contracts(
            origin, preregistration["components"]["api_contract"]
        )
    with subject_server() as (origin, _health):
        browser = browser_evidence(origin)

    api_result = evaluate_api(preregistration["components"]["api_contract"], api, None)
    browser_result = evaluate_browser(
        preregistration["components"]["browser_flow"], browser, None
    )
    evidence = {
        "spec_coverage": requirement_evidence(api_result, browser_result),
        "runtime_behavior": runtime,
        "api_contract": api,
        "browser_flow": browser,
        "diff_hygiene": diff_hygiene_evidence(builds),
    }
    score = execute_frozen_evaluation(plan, preregistration, evidence, {}, registry)
    tree = build_evidence_tree(case, plan, preregistration, score)
    tree["recording"] = {
        "kind": "real_local_execution",
        "remote_judge_used": False,
        "subject_directory_digest": directory_digest(SUBJECT),
    }
    tree.pop("evidence_digest", None)
    tree["evidence_digest"] = value_digest(tree)
    validation = validate_evaluation(
        case, spec_text, MODEL_ID, GENERATOR_CONFIG_DIGEST,
        plan, preregistration, score, tree, registry,
    )
    if validation["status"] != "pass":
        raise RuntimeError(f"fail-closed validation failed: {validation['violations']}")

    results = ROOT / "results"
    results.mkdir(exist_ok=True)
    atomic_write_json(results / "evidence_tree.json", tree)
    atomic_write_json(results / "evaluation.json", {
        "schema_version": "harnesseval_c.public_showcase_run.v1",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "case_id": case["case_id"],
        "subject_directory_digest": directory_digest(SUBJECT),
        "plan_digest": value_digest(plan),
        "preregistration_digest": preregistration["artifact_digest"],
        "remote_judge_used": False,
        "score": score,
        "validation": validation,
        "evidence_tree_digest": tree["evidence_digest"],
    })
    (results / "summary.md").write_text(
        render_summary(score, tree, directory_digest(SUBJECT)), encoding="utf-8"
    )
    print(json.dumps({
        "status": "pass",
        "case_id": case["case_id"],
        "core": score["core_score"],
        "observation": score["observation_score"],
        "final": score["final_score"],
        "evidence_tree": "examples/readlater/results/evidence_tree.json",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
