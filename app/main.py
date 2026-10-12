from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.auth import get_user
from app.schemas import IngestRequest, AskRequest, AgentRequest, AgentResponse
from app.pipeline import (JOBS, validate_url, ingest_repo, list_repos,
                          delete_repo, repo_key)
from app.chains.qa_chains import ask
from app.agents.explain_agent import explain
from app.agents.change_agent import suggest_change
from app.agents.test_agent import suggest_tests
from app.ratelimit import limit_user

app = FastAPI(title="CodeMind AI")
app.mount("/static", StaticFiles(directory="static"), name="static")


def run_safely(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        msg = str(e)
        if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "rate_limit" in msg.lower():
            raise HTTPException(429, "Rate limit exceeded. Wait one minute and try again.")
        raise HTTPException(500, f"An error occurred: {msg[:300]}")


@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest", status_code=202)
def ingest(req: IngestRequest, bg: BackgroundTasks, uid: str = Depends(get_user)):
    try:
        name = validate_url(req.url)
    except ValueError as e:
        raise HTTPException(400, str(e))

    key = repo_key(uid, name)
    if JOBS.get(key, {}).get("status") in {"queued", "cloning", "reading", "indexing"}:
        raise HTTPException(409, "This repository is already being indexed.")

    JOBS[key] = {"status": "queued"}
    bg.add_task(ingest_repo, req.url, name, uid)
    return {"repo": name, "status": "queued"}


@app.get("/ingest/{name}")
def ingest_status(name: str, uid: str = Depends(get_user)):
    job = JOBS.get(repo_key(uid, name))
    if not job:
        raise HTTPException(404, "No ingestion job was found for this repository.")
    return job


@app.get("/repos")
def repos(uid: str = Depends(get_user)):
    return run_safely(list_repos, uid)


@app.delete("/repos/{name}")
def remove_repo(name: str, uid: str = Depends(get_user)):
    return {"deleted_chunks": run_safely(delete_repo, uid, name)}


@app.post("/ask", response_model=AgentResponse)
def ask_endpoint(req: AskRequest, uid: str = Depends(limit_user)):
    return run_safely(ask, req.question, repo=repo_key(uid, req.repo), file=req.file)


@app.post("/explain", response_model=AgentResponse)
def explain_endpoint(req: AgentRequest, uid: str = Depends(limit_user)):
    return run_safely(explain, req.task, file=req.file, repo=repo_key(uid, req.repo))


@app.post("/change", response_model=AgentResponse)
def change_endpoint(req: AgentRequest, uid: str = Depends(limit_user)):
    return run_safely(suggest_change, req.task, file=req.file, repo=repo_key(uid, req.repo))


@app.post("/tests", response_model=AgentResponse)
def tests_endpoint(req: AgentRequest, uid: str = Depends(limit_user)):
    return run_safely(suggest_tests, req.task, file=req.file, repo=repo_key(uid, req.repo))
