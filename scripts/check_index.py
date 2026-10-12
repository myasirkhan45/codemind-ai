from collections import Counter
from app.vectorstore.chroma_store import get_store

metas = get_store().get(include=["metadatas"])["metadatas"]

print("Total chunks:", len(metas))
print("Repos:", Counter(m.get("repo") for m in metas))
print("Languages:", Counter(m.get("language") for m in metas))
print("Backslash wale paths:", sum("\\" in m["source"] for m in metas))
print("Sample:", metas[0])