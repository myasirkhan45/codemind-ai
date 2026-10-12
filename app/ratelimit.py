import time
from collections import defaultdict, deque

from fastapi import Depends, HTTPException

from app.auth import get_user

_hits: dict[str, deque] = defaultdict(deque)


def limit_user(uid: str = Depends(get_user), limit: int = 8, window: int = 60) -> str:
    """Limit each user to eight AI requests per minute."""
    now = time.time()
    q = _hits[uid]
    while q and now - q[0] > window:
        q.popleft()
    if len(q) >= limit:
        raise HTTPException(429, "You have reached the request limit. Please wait a minute and try again.")
    q.append(now)
    return uid
