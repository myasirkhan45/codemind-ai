from app.agents.base import run_agent

SYSTEM = """You are CodeMind AI, an expert code assistant.
Answer the question ONLY using the code context.
If the answer is not in the context, say "I could not find this information in the provided code context."
Always mention the file names and function or class names you used."""


def ask(question: str, repo: str | None = None, file: str | None = None, k: int = 6) -> dict:
    return run_agent(SYSTEM, question, k=k, file=file, repo=repo)
