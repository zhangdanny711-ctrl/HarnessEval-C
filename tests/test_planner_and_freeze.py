from copy import deepcopy

import pytest

from harnesseval_c.planner import freeze_plan, planner_input_digest, validate_plan
from harnesseval_c.skills import default_registry


def case():
    return {"case_id": "demo", "taxonomy": {"probe_family": "existing_feature_build"},
            "model_facing": {"task": "Build a task list", "initial_observation": "Empty app",
                             "resources": ["spec.md"]},
            "evaluation": {"required_skills": ["spec_coverage"]}}


def test_digest_covers_exact_semantic_planner_payload():
    registry = default_registry()
    original = case()
    same = deepcopy(original)
    changed = deepcopy(original)
    changed["model_facing"]["initial_observation"] = "App with a starter route"
    assert planner_input_digest(original, registry, "judge") == planner_input_digest(same, registry, "judge")
    assert planner_input_digest(original, registry, "judge") != planner_input_digest(changed, registry, "judge")


def test_frozen_plan_requires_configured_skills_and_digest():
    registry = default_registry()
    plan = freeze_plan(case(), registry, {"selected_skills": [
        {"skill_id": "spec_coverage"}, {"skill_id": "code_quality"}]}, "judge")
    validate_plan(plan, case(), registry, "judge")
    plan["input_digest"] = "tampered"
    with pytest.raises(ValueError, match="digest"):
        validate_plan(plan, case(), registry, "judge")

