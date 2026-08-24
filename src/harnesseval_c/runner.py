"""Execute a frozen plan against preregistered evidence inputs."""

from __future__ import annotations

from typing import Any

from .registry import SkillRegistry
from .scoring import score_case


def execute_frozen_evaluation(plan: dict[str, Any], preregistration: dict[str, Any],
                              evidence: dict[str, Any], judge_scores: dict[str, float | None],
                              registry: SkillRegistry) -> dict[str, Any]:
    if preregistration.get("case_id") != plan.get("case_id"):
        raise ValueError("plan and preregistration case mismatch")
    results = []
    components = preregistration.get("components") or {}
    for selected in plan.get("selected_skills") or []:
        skill_id = selected["skill_id"]
        try:
            result = registry.get(skill_id).evaluator(
                components.get(skill_id) or {}, evidence.get(skill_id) or {}, judge_scores.get(skill_id))
            results.append({"skill_id": skill_id, **result})
        except Exception as exc:
            results.append({"skill_id": skill_id, "status": "invalid", "score": None,
                            "diagnostics": {"error_type": type(exc).__name__}})
    return score_case(plan, results)
