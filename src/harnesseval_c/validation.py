"""Independent fail-closed checks over frozen inputs, scores, and Evidence Trees."""

from __future__ import annotations

import copy
from typing import Any

from .io import value_digest
from .planner import validate_plan
from .preregistration import validate_preregistration
from .registry import SkillRegistry
from .scoring import score_case


def validate_evaluation(case: dict[str, Any], spec_text: str, model: str,
                        generator_config_digest: str, plan: dict[str, Any],
                        preregistration: dict[str, Any], score: dict[str, Any],
                        evidence_tree: dict[str, Any], registry: SkillRegistry) -> dict[str, Any]:
    violations = []
    for label, check in (
        ("plan", lambda: validate_plan(plan, case, registry, model)),
        ("preregistration", lambda: validate_preregistration(
            preregistration, case, spec_text, generator_config_digest)),
    ):
        try:
            check()
        except ValueError as exc:
            violations.append({"kind": f"invalid_{label}", "detail": str(exc)})
    recomputed = score_case(plan, score.get("skill_results") or [])
    for field in ("evaluation_status", "core_score", "observation_score", "final_score"):
        if score.get(field) != recomputed.get(field):
            violations.append({"kind": "score_mismatch", "detail": field})
    clone = copy.deepcopy(evidence_tree)
    digest = clone.pop("evidence_digest", None)
    if digest != value_digest(clone):
        violations.append({"kind": "evidence_digest_mismatch"})
    if (evidence_tree.get("headline") or {}).get("final_score") != score.get("final_score"):
        violations.append({"kind": "evidence_score_mismatch"})
    return {"status": "pass" if not violations else "fail", "violations": violations}

