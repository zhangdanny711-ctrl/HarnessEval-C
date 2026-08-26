# ReadLater recorded showcase

ReadLater is one completely fictional full-stack Case created for the public
HarnessEval-C repository. Unlike the Todo artifact walkthrough, this directory
contains a real local evaluation of the included subject implementation.

## What is evaluated

The [SPEC](spec/readlater.md) requires five behaviors: save an article, list the
queue, mark an article read, reject a blank title, and complete the same flow in
a browser. The subject is deliberately small: a Python standard-library HTTP
server with an in-memory store and a dependency-free HTML/JavaScript client.

## Frozen before execution

- [`case.json`](case.json) defines the single Case and required Skills.
- [`frozen/plan.json`](frozen/plan.json) selects Spec Coverage, Runtime Behavior,
  API Contract, Browser Flow, and deterministic Diff Hygiene.
- [`frozen/preregistration.json`](frozen/preregistration.json) binds five
  requirements, two build checks, one health check, four runtime probes, four
  API contracts, one six-step browser journey, and three quality conventions.

`freeze_case.py` uses only Case/SPEC/evaluator configuration. It never reads the
subject directory.

## Reproduce

From the repository root, with Python 3.11+, Node.js, npm, and Chrome installed:

```bash
npm install --prefix examples/readlater
python examples/readlater/freeze_case.py
python examples/readlater/run_evaluation.py
```

The browser journey runs headlessly with Playwright. Set `PLAYWRIGHT_CHANNEL`
to another locally installed Playwright browser channel if needed.

## Recorded result

- [`results/evaluation.json`](results/evaluation.json) contains the score and
  fail-closed validation result.
- [`results/evidence_tree.json`](results/evidence_tree.json) contains the real
  step-level deterministic evidence.
- [`results/summary.md`](results/summary.md) is the concise human-readable view.

The evaluation does not call a remote LLM judge. Diff Hygiene is a limited,
deterministic-only Observation based on five recorded checks; it is not
presented as semantic code review. The separate Code Quality Skill remains
fail-closed unless its required semantic judgment is present.
