import re
import shutil
from collections import Counter

from app.ingestion.loader import clone_repo, load_code_files
from app.ingestion.chunker import split_docs
from app.vectorstore.chroma_store import index_chunks, get_store
from app.vectorstore.chroma_store import index_chunks, get_store, get_all

GITHUB_RE = re.compile(r"^https://github\.com/([\w.-]+)/([\w.-]+?)(?:\.git)?/?$")
MAX_CHUNKS = 800
JOBS: dict[str, dict] = {}   # {"<uid>__<repo>": {"status": ...}}


def repo_key(uid: str, name: str) -> str:
    """Har user ki repo ka apna unique naam: <uid>__<repo>."""
    return f"{uid}__{name}"


def validate_url(url: str) -> str:
    """Validate a GitHub URL and return an owner-qualified, URL-safe repo name."""
    m = GITHUB_RE.match(url.strip())
    if not m:
        raise ValueError("Only https://github.com/<user>/<repo> URLs are supported.")
    owner, name = m.groups()
    if owner.startswith(".") or name.startswith("."):
        raise ValueError("Invalid repository name.")
    return f"{owner}__{name}"


def ingest_repo(url: str, name: str, uid: str) -> None:
    """Background mein chalta hai: download, read, chunk, index."""
    key = repo_key(uid, name)
    path = None
    try:
        JOBS[key] = {"status": "cloning"}
        path = clone_repo(url)

        JOBS[key] = {"status": "reading"}
        docs = load_code_files(path)
        if not docs:
            JOBS[key] = {"status": "failed", "error": "No supported code files were found."}
            return

        for d in docs:                       # har chunk par owner ki mohar
            d.metadata["repo"] = key
            d.metadata["owner"] = uid

        chunks = split_docs(docs)
        if len(chunks) > MAX_CHUNKS:
            JOBS[key] = {
                "status": "failed",
                "error": f"Repository is too large ({len(chunks)} chunks, limit {MAX_CHUNKS}).",
            }
            return

        JOBS[key] = {"status": "indexing", "files": len(docs), "chunks": len(chunks)}
        index_chunks(chunks)
        JOBS[key] = {"status": "done", "files": len(docs), "chunks": len(chunks)}
    except Exception as e:
        JOBS[key] = {"status": "failed", "error": str(e)[:300]}
    finally:
        if path:                             # index ho gaya, ab download ki hui files ki zaroorat nahi
            shutil.rmtree(path, ignore_errors=True)


def _fetch_all(where: dict, page: int = 300):
    """Saare matching records pages mein (cloud ki limits se bachne ke liye)."""
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


def list_repos(uid: str) -> dict[str, int]:
    _, metas = get_all(where={"owner": uid})
    return dict(Counter(m["repo"].split("__", 1)[1] for m in metas))


def delete_repo(uid: str, name: str) -> int:
    key = repo_key(uid, name)
    ids, _ = get_all(where={"$and": [{"owner": uid}, {"repo": key}]})
    store = get_store()
    for i in range(0, len(ids), 100):
        store.delete(ids=ids[i:i + 100])
    JOBS.pop(key, None)
    return len(ids)
