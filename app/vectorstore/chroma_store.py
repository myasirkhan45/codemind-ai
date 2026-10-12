import time
from functools import lru_cache

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import (CHROMA_DIR, GOOGLE_API_KEY,
                        CHROMA_API_KEY, CHROMA_TENANT, CHROMA_DATABASE)


@lru_cache(maxsize=1)
def get_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=GOOGLE_API_KEY,
    )


@lru_cache(maxsize=1)
def get_store():
    if CHROMA_API_KEY:   # production: Chroma Cloud
        return Chroma(
            collection_name="codebase",
            embedding_function=get_embeddings(),
            chroma_cloud_api_key=CHROMA_API_KEY,
            tenant=CHROMA_TENANT,
            database=CHROMA_DATABASE,
        )
    return Chroma(                      # laptop: local folder
        collection_name="codebase",
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_DIR,
    )


def get_all(where=None, page=300):
    """Retrieve all matching records in pages to stay within cloud limits."""
    store = get_store()
    ids, metas, offset = [], [], 0
    while True:
        r = store.get(where=where, include=["metadatas"], limit=page, offset=offset)
        ids += r["ids"]
        metas += r["metadatas"]
        if len(r["ids"]) < page:
            break
        offset += page
    return ids, metas


def index_chunks(chunks, batch_size=20, pause=16) -> int:
    store = get_store()
    total = len(chunks)

    ids = [f"{chunks[0].metadata['repo']}-chunk-{i}" for i in range(total)]
    existing = set()
    for i in range(0, total, 100):
        existing |= set(store.get(ids=ids[i:i + 100])["ids"])

    for i in range(0, total, batch_size):
        batch = chunks[i:i + batch_size]
        batch_ids = ids[i:i + batch_size]

        if all(b in existing for b in batch_ids):
            continue

        for attempt in range(5):
            try:
                store.add_documents(batch, ids=batch_ids)
                break
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    time.sleep(60)
                else:
                    raise
        else:
            raise RuntimeError("Embedding failed after 5 retries.")

        time.sleep(pause)

    return total


def search(query: str, k: int = 4):
    return get_store().similarity_search(query, k=k)
