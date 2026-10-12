import time
from app.agents.explain_agent import explain
from app.agents.change_agent import suggest_change
from app.agents.test_agent import suggest_tests

REPO = "flask"
FILE = "src/flask/sansio/app.py"


def show(title, result):
    print(f"\n{'=' * 10} {title} {'=' * 10}")
    print(result["answer"])
    print("\nSOURCES:", result["sources"])


show("EXPLAIN", explain("Explain how the add_url_rule method works", file=FILE, repo=REPO))
time.sleep(20)   # Stay within Groq's 8,000-token-per-minute limit.
show("CHANGE", suggest_change("Add logging inside the add_url_rule method", file=FILE, repo=REPO))
time.sleep(20)
show("TEST", suggest_tests("Write tests for the add_url_rule method", file=FILE, repo=REPO))
