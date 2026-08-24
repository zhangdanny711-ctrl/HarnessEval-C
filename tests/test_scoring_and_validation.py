from copy import deepcopy

from harnesseval_c.io import value_digest
from harnesseval_c.planner import freeze_plan
from harnesseval_c.preregistration import freeze_preregistration
from harnesseval_c.report import build_evidence_tree
from harnesseval_c.runner import execute_frozen_evaluation
from harnesseval_c.scoring import score_case
from harnesseval_c.skills import default_registry
from harnesseval_c.validation import validate_evaluation


def fixtures():
    registry = default_registry()
    case = {"case_id": "demo", "taxonomy": {"probe_family": "existing_feature_build"},
            "model_facing": {"task": "Task list", "initial_observation": "Empty", "resources": []},
            "evaluation": {"required_skills": ["spec_coverage"]}}
    plan = freeze_plan(case, registry, {"selected_skills": [
        {"skill_id": "spec_coverage"}, {"skill_id": "code_quality"}]}, "judge")
    pre = freeze_preregistration(case, "SPEC", {
        "spec_coverage": {"requirements": [{"req_id": "R1"}]}, "code_quality": {}}, "generator")
    evidence = {"spec_coverage": {"requirements": {"R1": {"passed": True}}},
                "code_quality": {"notes": []}}
    score = execute_frozen_evaluation(plan, pre, evidence,
                                      {"spec_coverage": 1.0, "code_quality": 0.8}, registry)
    tree = build_evidence_tree(case, plan, pre, score)
    return registry, case, plan, pre, score, tree


def test_missing_score_bearing_skill_fails_closed():
    plan = {"case_id": "x", "selected_skills": [
        {"skill_id": "a", "role": "core"}, {"skill_id": "b", "role": "observation"}]}
    score = score_case(plan, [{"skill_id": "a", "status": "ok", "score": 1.0}])
    assert score["evaluation_status"] == "invalid"
    assert score["final_score"] is None


def test_complete_evaluation_validates_and_tampering_fails():
    registry, case, plan, pre, score, tree = fixtures()
    result = validate_evaluation(case, "SPEC", "judge", "generator", plan, pre, score, tree, registry)
    assert result == {"status": "pass", "violations": []}
    broken = deepcopy(tree)
    broken["headline"]["final_score"] = 0.1
    assert validate_evaluation(case, "SPEC", "judge", "generator", plan, pre, score, broken, registry)["status"] == "fail"


def test_preregistration_artifact_digest_detects_changes():
    registry, case, plan, pre, score, tree = fixtures()
    pre["components"]["code_quality"]["extra"] = True
    result = validate_evaluation(case, "SPEC", "judge", "generator", plan, pre, score, tree, registry)
    assert any(v["kind"] == "invalid_preregistration" for v in result["violations"])

