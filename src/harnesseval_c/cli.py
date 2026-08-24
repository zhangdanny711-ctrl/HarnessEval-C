"""Small public command-line interface."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .io import read_json
from .planner import validate_plan
from .preregistration import validate_preregistration
from .skills import default_registry


def verify_example(root: Path) -> None:
    manifest = read_json(root / "manifest.json")
    registry = default_registry()
    for case in manifest["cases"]:
        case_id = case["case_id"]
        spec = (root / case["spec_path"]).read_text(encoding="utf-8")
        plan = read_json(root / "frozen" / "plans" / f"{case_id}.json")
        prereg = read_json(root / "frozen" / "preregistrations" / f"{case_id}.json")
        validate_plan(plan, case, registry, manifest["judge_model"])
        validate_preregistration(prereg, case, spec, manifest["generator_config_digest"])
    print(json.dumps({"status": "pass", "cases": len(manifest["cases"])}))


def main() -> None:
    parser = argparse.ArgumentParser(prog="harnesseval-c")
    sub = parser.add_subparsers(dest="command", required=True)
    verify = sub.add_parser("verify-example")
    verify.add_argument("root", type=Path)
    args = parser.parse_args()
    if args.command == "verify-example":
        verify_example(args.root)

