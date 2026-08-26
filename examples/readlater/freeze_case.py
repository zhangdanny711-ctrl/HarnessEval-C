"""Freeze the single ReadLater plan and preregistration without rollout input."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPOSITORY = ROOT.parents[1]
sys.path.insert(0, str(REPOSITORY / "src"))

from harnesseval_c.io import atomic_write_json, read_json  # noqa: E402
from harnesseval_c.planner import freeze_plan  # noqa: E402
from harnesseval_c.preregistration import freeze_preregistration  # noqa: E402
from harnesseval_c.skills import default_registry  # noqa: E402
from showcase_config import GENERATOR_CONFIG_DIGEST, MODEL_ID  # noqa: E402


def components() -> dict:
    envelope = ["requestId", "created", "code", "message"]
    return {
        "spec_coverage": {"requirements": [
            {"req_id": "R1", "text": "Save an article with a non-blank title"},
            {"req_id": "R2", "text": "List saved articles"},
            {"req_id": "R3", "text": "Mark a saved article as read"},
            {"req_id": "R4", "text": "Reject blank or whitespace-only titles"},
            {"req_id": "R5", "text": "Complete the same flow through the browser UI"},
        ]},
        "runtime_behavior": {
            "build_steps": ["python_compile", "javascript_syntax"],
            "health_checks": ["http_health"],
            "probes": [
                {"id": "P1_SAVE", "method": "POST", "path": "/api/articles",
                 "body": {"title": "Runtime Probe Article"},
                 "expect": {"http_status": 201}},
                {"id": "P2_LIST", "method": "GET", "path": "/api/articles",
                 "expect": {"http_status": 200}},
                {"id": "P3_MARK_READ", "method": "PATCH", "path": "/api/articles/1/read",
                 "expect": {"http_status": 200}},
                {"id": "P4_REJECT_BLANK", "method": "POST", "path": "/api/articles",
                 "body": {"title": "   "}, "expect": {"http_status": 400}},
            ],
        },
        "api_contract": {
            "default_envelope_fields": envelope,
            "contracts": [
                {"id": "A1_SAVE", "method": "POST", "path": "/api/articles",
                 "request": {"title": "API Contract Article"},
                 "expect": {"http_status": 201,
                            "equals": {"code": "CREATED", "data.title": "API Contract Article"}}},
                {"id": "A2_LIST", "method": "GET", "path": "/api/articles",
                 "expect": {"http_status": 200, "equals": {"code": "OK"},
                            "items_path": "data", "min_items": 1}},
                {"id": "A3_MARK_READ", "method": "PATCH", "path": "/api/articles/1/read",
                 "expect": {"http_status": 200,
                            "equals": {"code": "OK", "data.read": True}}},
                {"id": "A4_REJECT_BLANK", "method": "POST", "path": "/api/articles",
                 "request": {"title": "  "},
                 "expect": {"http_status": 400, "equals": {"code": "INVALID_INPUT"},
                            "message_contains": ["title", "required"]}},
            ],
        },
        "browser_flow": {
            "journeys": [{
                "journey_id": "J1",
                "description": "Save an article, see it in the queue, and mark it read",
                "steps": [
                    {"kind": "goto", "url": "/"},
                    {"kind": "fill", "selector": "[data-testid=article-title]",
                     "value": "Browser Evidence Article"},
                    {"kind": "click", "selector": "[data-testid=save-article]"},
                    {"kind": "expect_text", "selector": "[data-testid=reading-queue]",
                     "text": "Browser Evidence Article"},
                    {"kind": "click",
                     "selector": "[data-title='Browser Evidence Article'] [data-testid=mark-read]"},
                    {"kind": "expect_visible",
                     "selector": "[data-title='Browser Evidence Article'][data-read='true']"},
                ],
            }],
        },
        "diff_hygiene": {
            "semantic_required": False,
            "conventions": [
                "Keep the subject dependency-free",
                "Exclude placeholder and dynamic-evaluation constructs",
                "Limit the subject snapshot to files required by the SPEC",
            ]
        },
    }


def main() -> None:
    case = read_json(ROOT / "case.json")
    spec_text = (ROOT / "spec" / "readlater.md").read_text(encoding="utf-8")
    registry = default_registry()
    selected = [
        {"skill_id": "spec_coverage", "reason": "Trace all five frozen SPEC requirements"},
        {"skill_id": "runtime_behavior", "reason": "Build, boot, and exercise state transitions"},
        {"skill_id": "api_contract", "reason": "Verify the four frozen HTTP contracts"},
        {"skill_id": "browser_flow", "reason": "Exercise the user-visible save/read flow"},
        {"skill_id": "diff_hygiene", "reason": "Record deterministic subject-scope hygiene checks"},
    ]
    plan = freeze_plan(case, registry, {"selected_skills": selected}, MODEL_ID)
    preregistration = freeze_preregistration(
        case, spec_text, components(), GENERATOR_CONFIG_DIGEST
    )
    atomic_write_json(ROOT / "frozen" / "plan.json", plan)
    atomic_write_json(ROOT / "frozen" / "preregistration.json", preregistration)
    print(f"frozen plan input digest: {plan['input_digest']}")
    print(f"frozen preregistration digest: {preregistration['artifact_digest']}")


if __name__ == "__main__":
    main()
