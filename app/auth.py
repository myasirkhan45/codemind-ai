from fastapi import Header, HTTPException
from google.auth.transport import requests as g_requests
from google.oauth2 import id_token

from app.config import FIREBASE_PROJECT_ID

_request = g_requests.Request()


def get_user(authorization: str | None = Header(default=None)) -> str:
    """Verify the Firebase token and return the user's UID."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Authentication is required.")

    token = authorization.split(" ", 1)[1]
    try:
        claims = id_token.verify_firebase_token(
            token, _request,
            audience=FIREBASE_PROJECT_ID,
            clock_skew_in_seconds=10,   # Allow minor clock differences between the client and server.
        )
    except Exception:
        raise HTTPException(401, "The token is invalid or expired. Please sign in again.")

    if not claims or "sub" not in claims:
        raise HTTPException(401, "The authentication token is invalid.")
    return claims["sub"]
