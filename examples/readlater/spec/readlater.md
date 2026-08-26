# ReadLater — fictional public evaluation SPEC

Build a minimal full-stack reading queue. The application stores data in memory;
durable persistence, authentication, databases, deployment, and frameworks are
out of scope.

## Required behavior

1. A user can save an article with a non-blank title.
2. A user can list all saved articles.
3. A user can mark a saved article as read.
4. Blank or whitespace-only titles are rejected.
5. A browser UI exposes the same save, list, and mark-read flow.

## HTTP contract

- `GET /health` returns a healthy response.
- `GET /api/articles` lists articles.
- `POST /api/articles` accepts `{ "title": "..." }`.
- `PATCH /api/articles/{id}/read` marks an article as read.

Every JSON response contains `requestId`, `created`, `code`, and `message`.
Successful payloads are returned in `data`.
