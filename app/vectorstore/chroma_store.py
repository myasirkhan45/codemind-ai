import time
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import CHROMA_DIR, GOOGLE_API_KEY


def get_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=GOOGLE_API_KEY,
    )


def get_store():
    return Chroma(
        collection_name="codebase",
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_DIR,
    )


def index_chunks(chunks, batch_size=20, pause=16) -> int:
    store = get_store()
    total = len(chunks)

    # har chunk ko fixed ID do (resume karne ke liye)
    ids = [f"{chunks[0].metadata['repo']}-chunk-{i}" for i in range(total)]
    existing = set(store.get(ids=ids)["ids"])
    print(f"Pehle se indexed: {len(existing)}")

    for i in range(0, total, batch_size):
        batch = chunks[i : i + batch_size]
        batch_ids = ids[i : i + batch_size]

        # agar ye batch pehle ho chuka, skip
        if all(b in existing for b in batch_ids):
            print(f"Skip {min(i + batch_size, total)}/{total}")
            continue

        for attempt in range(5):
            try:
                store.add_documents(batch, ids=batch_ids)
                break
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    print("Rate limit hit, 60 sec wait...")
                    time.sleep(60)
                else:
                    raise
        else:
            raise RuntimeError("5 retries ke baad bhi fail")

        print(f"Indexed {min(i + batch_size, total)}/{total}")
        time.sleep(pause)

    return total


def search(query: str, k: int = 4):
    return get_store().similarity_search(query, k=k)