from harnesseval_c.http_assertions import check_http_response
from harnesseval_c.skills.api_contract import evaluate as api
from harnesseval_c.skills.browser_flow import evaluate as browser
from harnesseval_c.skills.observation import evaluate as observation
from harnesseval_c.skills.runtime_behavior import evaluate as runtime
from harnesseval_c.skills import default_registry


def test_message_contains_checks_every_substring_and_envelope_is_configurable():
    expectation = {"http_status": 400, "message_contains": ["title", "required"]}
    fields = ["requestId", "created", "code", "message"]
    body = {"requestId": "r1", "created": "now", "code": "INVALID", "message": "title is required"}
    assert check_http_response(400, body, expectation, fields)["passed"] is True
    assert check_http_response(400, {**body, "message": "title invalid"}, expectation, fields)["passed"] is False
    assert check_http_response(400, {"code": "INVALID", "message": "title is required"}, expectation, fields)["passed"] is False


def test_runtime_semantic_judge_cannot_override_objective_failures():
    failed_build = runtime({}, {"builds": [{"passed": False}], "health": [{"passed": True}],
                                "probes": [{"passed": True}]}, 1.0)
    failed_boot = runtime({}, {"builds": [{"passed": True}], "health": [{"passed": False}],
                               "probes": [{"passed": True}]}, 1.0)
    failed_probe = runtime({}, {"builds": [{"passed": True}], "health": [{"passed": True}],
                                "probes": [{"passed": True}, {"passed": False}]}, 1.0)
    assert failed_build["score"] == 0.2
    assert failed_boot["score"] == 0.4
    assert failed_probe["score"] == 0.75


def test_browser_actions_do_not_compensate_for_failed_assertion():
    steps = [{"kind": kind, "passed": True} for kind in ["goto", "click", "fill", "select", "hover"]]
    steps.append({"kind": "expect_text", "passed": False})
    result = browser({}, {"journeys": [{"journey_id": "J1", "steps": steps}]}, 1.0)
    assert result["score"] == 0.0
    assert result["evidence"]["journeys"][0]["action_pass_rate"] == 1.0


def test_api_score_is_bounded_by_contract_pass_rate():
    config = {"default_envelope_fields": ["code", "message"], "contracts": [
        {"id": "ok", "expect": {"http_status": 200}},
        {"id": "bad", "expect": {"http_status": 200}}]}
    evidence = {"responses": {"ok": {"status": 200, "body": {"code": "OK", "message": "ok"}},
                              "bad": {"status": 500, "body": {"code": "ERR", "message": "bad"}}}}
    assert api(config, evidence, 1.0)["score"] == 0.5


def test_semantic_required_observation_fails_closed_without_semantic_score():
    evidence = {"checks": [
        {"id": "syntax", "passed": True},
        {"id": "source_hygiene", "passed": True},
    ]}
    result = observation({"semantic_required": True}, evidence, None)
    assert result["status"] == "invalid"
    assert result["score"] is None


def test_observation_without_any_evidence_fails_closed():
    result = observation({"semantic_required": False}, {}, None)
    assert result["status"] == "invalid"
    assert result["score"] is None


def test_deterministic_only_observation_still_scores_without_semantic_score():
    evidence = {"checks": [
        {"id": "syntax", "passed": True},
        {"id": "source_hygiene", "passed": True},
    ]}
    result = observation({"semantic_required": False}, evidence, None)
    assert result["status"] == "ok"
    assert result["score"] == 1.0
    assert result["metrics"]["semantic_judge_used"] is False


def test_semantic_judgment_can_only_lower_deterministic_observation():
    evidence = {"checks": [{"id": "syntax", "passed": True}]}
    result = observation({"semantic_required": True}, evidence, 0.6)
    assert result["status"] == "ok"
    assert result["score"] == 0.6


def test_registry_enforces_semantic_review_for_code_quality():
    evaluator = default_registry().get("code_quality").evaluator
    result = evaluator(
        {"semantic_required": False},
        {"checks": [{"id": "syntax", "passed": True}]},
        None,
    )
    assert result["status"] == "invalid"
    assert result["score"] is None


def test_code_quality_fails_closed_without_deterministic_checks():
    evaluator = default_registry().get("code_quality").evaluator
    for evidence in ({}, {"checks": []}):
        result = evaluator({}, evidence, 1.0)
        assert result["status"] == "invalid"
        assert result["score"] is None


def test_code_quality_with_both_evidence_sources_is_bounded_normally():
    evaluator = default_registry().get("code_quality").evaluator
    result = evaluator(
        {},
        {"checks": [
            {"id": "syntax", "passed": True},
            {"id": "source_hygiene", "passed": False},
        ]},
        1.0,
    )
    assert result["status"] == "ok"
    assert result["score"] == 0.5
