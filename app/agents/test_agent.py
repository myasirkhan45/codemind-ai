from collections import Counter
from app.agents.base import retrieve, generate

# Test frameworks by programming language.
TEST_FRAMEWORKS = {
    "python": "pytest",
    "js": "Jest",
    "ts": "Jest (TypeScript)",
    "java": "JUnit 5",
    "go": "the standard testing package (go test)",
    "cpp": "GoogleTest",
    "rust": "the built-in test framework (cargo test, #[test])",
    "csharp": "xUnit",
    "php": "PHPUnit",
    "ruby": "RSpec",
    "kotlin": "JUnit 5",
    "c": "plain assert-based tests",
}

TEMPLATE = """You are CodeMind Test Agent.
The code in the context is written in {language}. Write tests using {framework}.
Rules:
- Test the REAL code by importing it from its module/package. NEVER copy or
  re-implement code from the context into a dummy or mock class.
- Use the EXACT class and function names from the context. Never rename them.
- Do not access private members (names starting with underscore).
- Cover: normal case, edge case, error case.
- Only assert behavior you can see in the context. If unsure, skip that test.
- Short comment above each test. Finish every test completely.
- If the context has too little code, list what is missing at the end.

- NEVER use reflection (getDeclaredField, getDeclaredMethod, setAccessible) or any trick to
  reach private members. If something can only be tested through private members, skip it
  and list it under "Not tested".
- NEVER replace fields of the object under test after construction.
- If the code depends on a platform runtime (Android, browser DOM), say at the top which test
  setup is needed (for example Robolectric or jsdom). Do not fake the platform.
- End with an "Assumptions" section listing anything you assumed that is not visible in the context.
- Your explanation must match your code. Do not claim things the code does not do.
"""


def suggest_tests(task: str, file: str | None = None, repo: str | None = None,
                  k: int = 6) -> dict:
    # 1. Retrieve relevant code chunks.
    docs = retrieve(task, k=k, file=file, repo=repo)
    if not docs:
        return {
            "answer": "No indexed code chunks were found. Check the repository and file name.",
            "sources": [],
        }

    # 2. Select the language represented by the most retrieved chunks.
    lang = Counter(d.metadata["language"] for d in docs).most_common(1)[0][0]
    framework = TEST_FRAMEWORKS.get(lang, "the most common test framework for this language")

    # 3. Build the prompt and generate the response.
    system = TEMPLATE.format(language=lang, framework=framework)
    return generate(system, task, docs)
