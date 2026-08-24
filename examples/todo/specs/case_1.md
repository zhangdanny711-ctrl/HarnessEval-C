# Case 1 — Basic tasks

Build a tiny task application. A visitor can create a task with a non-empty title,
see it in the list, and mark it complete. The JSON API returns a common envelope
with `requestId`, `created`, `code`, and `message`; payloads are stored in `data`.

Required API behavior:

- `GET /api/tasks` lists tasks.
- `POST /api/tasks` creates a task and rejects blank titles.
- `PATCH /api/tasks/{id}` updates `completed`.

The browser flow must demonstrate creation and completion through visible UI.

