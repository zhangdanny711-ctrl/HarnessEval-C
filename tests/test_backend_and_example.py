import json
from pathlib import Path
from types import SimpleNamespace

from harnesseval_c.backends import JudgeBackend, JudgeConfig
from harnesseval_c.cli import verify_example


def test_curl_backend_keeps_key_out_of_arguments_and_result(monkeypatch, tmp_path):
    captured = {}
    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        captured["stdin"] = kwargs["input"]
        return SimpleNamespace(returncode=0, stdout=json.dumps({
            "model": "fictional-judge", "usage": {"total_tokens": 4},
            "choices": [{"message": {"content": '{"score": 0.5}'}}]}), stderr="")
    monkeypatch.setattr("harnesseval_c.backends.subprocess.run", fake_run)
    backend = JudgeBackend(JudgeConfig("https://judge.invalid/v1", "TOP-SECRET", "fictional-judge"))
    result = backend.infer([{"role": "user", "content": "return JSON"}])
    assert result["parsed"] == {"score": 0.5}
    assert result["response_model"] == "fictional-judge"
    assert result["usage"] == {"total_tokens": 4}
    assert "TOP-SECRET" not in " ".join(captured["argv"])
    assert "TOP-SECRET" not in json.dumps(result)


def test_fictional_example_frozen_artifacts_verify(capsys):
    root = Path(__file__).parents[1] / "examples" / "todo"
    verify_example(root)
    assert json.loads(capsys.readouterr().out)["status"] == "pass"

