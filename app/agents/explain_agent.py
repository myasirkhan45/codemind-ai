from app.agents.base import run_agent

SYSTEM = """You are CodeMind Explain Agent.
Explain the code from the context to a beginner developer.
Rules:
- Use ONLY the given context. If something is missing, write "Not in provided context".
- Never write "implied" or guess.
- Mention file names and function/class names.
- Format: 1) One-line summary  2) Step-by-step flow  3) Simple analogy
"""


def explain(task: str, file: str | None = None, repo: str | None = None,
            k: int = 6) -> dict:
    return run_agent(SYSTEM, task, k=k, file=file, repo=repo)
