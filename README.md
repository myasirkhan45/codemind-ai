# Codebase Assistant

Codebase Assistant indexes source files into a local Chroma vector store and
uses the retrieved code as context for answers, explanations, change suggestions,
and test suggestions.

## Setup

Install the dependencies and set the provider keys in `.env`:

```text
GOOGLE_API_KEY=...
GROQ_API_KEY=...
```

Google's embedding API is used during indexing and retrieval. Groq is used to
generate answers. Index a repository with:

```powershell
python -m scripts.ingest_test
```

Start the API from the project root:

```powershell
uvicorn app.main:app --reload
```

Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

## Endpoints

- `GET /health` reports API process readiness.
- `POST /ask` accepts `{"question": "How does routing work?", "k": 4}`.
- `POST /explain`, `/change`, and `/tests` accept a `task`, with optional
  `file`, `repo`, and `k` fields. For example:

```json
{
  "task": "Explain how add_url_rule works",
  "repo": "flask",
  "file": "src/flask/sansio/app.py"
}
```

Agent endpoints return an `answer` and the indexed source paths used to create
it. `k` controls the number of retrieved chunks and is limited to 1–20.
