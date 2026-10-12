from fastapi import Header, HTTPException
from google.auth.transport import requests as g_requests
from google.oauth2 import id_token

from app.config import FIREBASE_PROJECT_ID

_request = g_requests.Request()


def get_user(authorization: str | None = Header(default=None)) -> str:
    """Firebase token verify karta hai aur user ki uid return karta hai."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Login zaroori hai.")

    token = authorization.split(" ", 1)[1]
    try:
        claims = id_token.verify_firebase_token(
            token, _request,
            audience=FIREBASE_PROJECT_ID,
            clock_skew_in_seconds=10,   # PC ki ghari thori aage peeche ho to bhi chale
        )
    except Exception:
        raise HTTPException(401, "Token galat ya expire hai. Dobara login karo.")

    if not claims or "sub" not in claims:
        raise HTTPException(401, "Token galat hai.")
    return claims["sub"]