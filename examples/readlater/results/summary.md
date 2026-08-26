# Recorded evaluation — ReadLater

This is a real local execution against the included fictional subject, not illustrative data.
No remote LLM judge or credential was used.

## Scores

| Skill | Role | Status | Score |
|---|---|---:|---:|
| `spec_coverage` | core | ok | 1.000000 |
| `runtime_behavior` | core | ok | 1.000000 |
| `api_contract` | core | ok | 1.000000 |
| `browser_flow` | core | ok | 1.000000 |
| `diff_hygiene` | observation | ok | 1.000000 |

- **Core:** 1.000000
- **Observation:** 1.000000
- **Final:** 1.000000
- **Validation:** valid

## Recorded evidence

- Two syntax/build commands executed locally.
- Three independent subject processes served Runtime, API, and Browser checks.
- Four stateful runtime probes and four API contracts executed over HTTP.
- One six-step browser journey executed in headless Chrome through Playwright.
- Five deterministic diff-hygiene checks supplied the Observation score.
- Subject directory digest: `16a4d253b4aca25d8e4cbb5d781ae8782affcb8945a58b52260b06961d76e10d`
- Evidence Tree digest: `5bb607a8eb12d6ee75b82db4a950ffad0759f67e84473cd986f87060b82b686e`

See [`evidence_tree.json`](evidence_tree.json) for step-level evidence.
