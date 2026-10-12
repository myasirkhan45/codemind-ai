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

## GitHub sign-in and repository picker

To enable GitHub login and the public repository picker:

1. Create a GitHub OAuth App. Set its callback URL to
   `https://codebaseassistant-2d455.firebaseapp.com/__/auth/handler`.
2. In Firebase Console, open **Authentication → Sign-in method → GitHub** and
   enable the provider using the OAuth App's client ID and client secret.
3. Keep the provider permission at `read:user`; the app requests this scope to
   identify the GitHub account and lists public repositories only.
4. Reload the app, sign in with GitHub or use **Connect GitHub** in the sidebar,
   then choose a repository and select **Index selected repository**.

The GitHub access token stays in browser memory and is used only to retrieve
the user's public repository list. Repository archives are downloaded through
GitHub's public archive endpoint; private repository access is not requested.

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
