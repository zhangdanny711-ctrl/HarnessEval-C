"""Case-only skill planning with digest-addressed freezing."""

from __future__ import annotations

from typing import Any

from .io import value_digest
from .registry import SkillRegistry

PLAN_SCHEMA = "harnesseval_c.skill_plan.v1"


def planner_payload(case: dict[str, Any], registry: SkillRegistry) -> dict[str, Any]:
    model_facing = case.get("model_facing") or {}
    return {
        "case_id": case["case_id"],
        "taxonomy": case["taxonomy"],
        "task": model_facing.get("task"),
        "initial_observation": model_facing.get("initial_observation"),
        "resources": model_facing.get("resources", []),
        "skill_catalog": registry.catalog(),
        "required_skills": (case.get("evaluation") or {}).get("required_skills", []),
    }


def planner_messages(case: dict[str, Any], registry: SkillRegistry) -> list[dict[str, str]]:
    import json
    return [
        {"role": "system", "content": "Select evaluation skills for this case. Return JSON only."},
        {"role": "user", "content": json.dumps(planner_payload(case, registry), sort_keys=True)},
    ]


def planner_input_digest(case: dict[str, Any], registry: SkillRegistry,
                         model: str, prompt_version: str = "planner.v1") -> str:
    return value_digest({"model": model, "prompt_version": prompt_version,
                         "messages": planner_messages(case, registry)})


def freeze_plan(case: dict[str, Any], registry: SkillRegistry,
                candidate: dict[str, Any], model: str) -> dict[str, Any]:
    required = list((case.get("evaluation") or {}).get("required_skills", []))
    selections = candidate.get("selected_skills") or []
    selected_ids = [item.get("skill_id") for item in selections if isinstance(item, dict)]
    if len(selected_ids) != len(set(selected_ids)):
        raise ValueError("planner selected duplicate skills")
    unknown = sorted(set(selected_ids) - set(registry.ids()))
    if unknown:
        raise ValueError(f"planner selected unknown skills: {unknown}")
    missing = sorted(set(required) - set(selected_ids))
    if missing:
        raise ValueError(f"planner omitted required skills: {missing}")
    normalized = []
    for item in selections:
        skill = registry.get(str(item["skill_id"]))
        role = str(item.get("role") or skill.role)
        if role != skill.role:
            raise ValueError(f"role mismatch for {skill.skill_id}")
        normalized.append({"skill_id": skill.skill_id, "role": role,
                           "reason": str(item.get("reason") or "selected for this case")})
    return {
        "schema_version": PLAN_SCHEMA,
        "case_id": case["case_id"],
        "input_digest": planner_input_digest(case, registry, model),
        "selected_skills": normalized,
        "validation": {"status": "ok", "selection_modified": False},
    }


def validate_plan(plan: dict[str, Any], case: dict[str, Any], registry: SkillRegistry,
                  model: str) -> None:
    if plan.get("schema_version") != PLAN_SCHEMA:
        raise ValueError("plan schema mismatch")
    if plan.get("case_id") != case.get("case_id"):
        raise ValueError("plan case mismatch")
    if plan.get("input_digest") != planner_input_digest(case, registry, model):
        raise ValueError("plan input digest mismatch")
    if (plan.get("validation") or {}).get("selection_modified") is not False:
        raise ValueError("plan selection was modified")
    freeze_plan(case, registry, {"selected_skills": plan.get("selected_skills")}, model)

