
from app.chains.qa_chains import ask

result = ask("How are errors handled in Flask?")

print("ANSWER:\n", result["answer"])
print("\nSOURCES:")
for s in result["sources"]:
    print(" -", s)