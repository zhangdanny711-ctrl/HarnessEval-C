"""Evidence Tree construction."""

from __future__ import annotations

from typing import Any

from .io import value_digest


def build_evidence_tree(case: dict[str, Any], plan: dict[str, Any],
                        preregistration: dict[str, Any], score: dict[str, Any]) -> dict[str, Any]:
    tree = {
        "schema_version": "harnesseval_c.evidence_tree.v1",
        "case_id": case["case_id"],
        "headline": {key: score.get(key) for key in (
            "evaluation_status", "core_score", "observation_score", "final_score")},
        "frozen_inputs": {"plan_digest": value_digest(plan),
                          "preregistration_digest": preregistration.get("artifact_digest")},
        "plan": plan.get("selected_skills") or [],
        "skills": [
            {"skill_id": item.get("skill_id"), "role": item.get("role"),
             "status": item.get("status"), "score": item.get("score"),
             "metrics": item.get("metrics") or {}, "evidence": item.get("evidence") or {},
             "diagnostics": item.get("diagnostics") or {}}
            for item in score.get("skill_results") or []
        ],
    }
    tree["evidence_digest"] = value_digest(tree)
    return tree

