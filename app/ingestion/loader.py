import io
import os
import re
import shutil
import zipfile

import requests

from langchain_core.documents import Document
from app.config import REPOS_DIR, CODE_EXTENSIONS, IGNORE_DIRS

MAX_FILE_BYTES = 200_000
MAX_ZIP_BYTES = 60 * 1024 * 1024         # Maximum archive download size.
MAX_UNZIPPED_BYTES = 250 * 1024 * 1024   # Maximum extracted archive size.

GITHUB_RE = re.compile(r"^https://github\.com/([\w.-]+)/([\w.-]+?)(?:\.git)?/?$")


def clone_repo(url: str) -> str:
    """Download a GitHub repository archive and extract it under data/repos/."""
    m = GITHUB_RE.match(url.strip())
    if not m:
        raise ValueError("Only https://github.com/<user>/<repo> URLs are supported.")
    owner, name = m.groups()

    path = os.path.join(REPOS_DIR, f"{owner}__{name}")
    if os.path.exists(path):
        return path

    r = requests.get(f"https://github.com/{owner}/{name}/archive/HEAD.zip",
                     stream=True, timeout=60)
    if r.status_code == 404:
        raise ValueError("Repository not found, or it is private.")
    r.raise_for_status()

    buf, size = io.BytesIO(), 0
    for part in r.iter_content(256 * 1024):
        size += len(part)
        if size > MAX_ZIP_BYTES:
            raise ValueError("Repository is too large to download.")
        buf.write(part)

    tmp = path + ".tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp, exist_ok=True)
    with zipfile.ZipFile(buf) as z:
        if sum(i.file_size for i in z.infolist()) > MAX_UNZIPPED_BYTES:
            raise ValueError("Repository is too large.")
        z.extractall(tmp)

    # Move the archive's top-level directory into the repository path.
    entries = os.listdir(tmp)
    root = os.path.join(tmp, entries[0]) if len(entries) == 1 else tmp
    shutil.move(root, path)
    shutil.rmtree(tmp, ignore_errors=True)
    return path


def load_code_files(repo_path: str) -> list[Document]:
    docs = []
    repo_name = os.path.basename(os.path.normpath(repo_path))

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in CODE_EXTENSIONS:
                continue

            full_path = os.path.join(root, file)
            if os.path.getsize(full_path) > MAX_FILE_BYTES:
                continue

            try:
                with open(full_path, encoding="utf-8") as f:
                    text = f.read()
            except Exception:
                continue

            if not text.strip():
                continue

            rel_path = os.path.relpath(full_path, repo_path).replace("\\", "/")
            docs.append(Document(
                page_content=text,
                metadata={
                    "source": rel_path,
                    "language": CODE_EXTENSIONS[ext],
                    "repo": repo_name,
                },
            ))
    return docs
