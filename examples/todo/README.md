# Fictional Todo benchmark

This example demonstrates artifact shape and evaluator configuration; it is not
an agent leaderboard and contains no rollout.

The `scaffold` directory is a deliberately incomplete, standard-library starter
with an HTTP API and browser UI. A subject is expected to modify a copy; the
starter itself is not presented as a passing solution.

- `todo_case_1` builds basic task creation, listing, validation, and completion.
- `todo_case_2` starts from the subject's own Case 1 snapshot, adds priority
  filtering, and freezes Case 1 replay checks through Regression Guard.
- `frozen/plans` contains case-only Skill selections.
- `frozen/preregistrations` contains requirements, probes, contracts, browser
  journeys, conventions, and protected anchors.
- `representative/evidence_tree.json` is marked `illustrative: true`.

Verify artifact digests and canonical structure with:

```bash
python -m harnesseval_c verify-example examples/todo
```
