import sys
from app.ingestion.loader import clone_repo, load_code_files
from app.ingestion.chunker import split_docs
from app.vectorstore.chroma_store import index_chunks
from app.agents.test_agent import suggest_tests

url = sys.argv[1]
path = clone_repo(url)
docs = load_code_files(path)
print("Files:", len(docs), "| Languages:", {d.metadata["language"] for d in docs})

chunks = split_docs(docs)
print("Chunks:", len(chunks))
index_chunks(chunks)

repo = docs[0].metadata["repo"]
file = docs[0].metadata["source"]
print("Repo:", repo, "| File:", file)

result = suggest_tests("Write unit tests for the main functions", file=file, repo=repo)
print(result["answer"])
print("SOURCES:", result["sources"])