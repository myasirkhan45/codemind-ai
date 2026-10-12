from app.ingestion.loader import clone_repo,load_code_files
from app.ingestion.chunker import split_docs
from app.vectorstore.chroma_store import index_chunks,search

path = clone_repo("https://github.com/pallets/flask")
docs = load_code_files(path)
print("Files:", len(docs))

chunks = split_docs(docs)
print("Chunks: ", len(chunks))

index_chunks(chunks)

for r in search("how does routing work?"):
    print(r.metadata["source"])
    print(r.page_content[:200],"\n---")
    
