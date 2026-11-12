"""Shared helpers for the GitHub OAuth endpoints.

The Vercel functions in ``api/`` are intentionally tiny: this module parses the
origin allow-list, builds the GitHub authorize URL and exchanges the OAuth code
for an access token.  No state is stored on the server.
"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request

AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
TOKEN_URL = "https://github.com/login/oauth/access_token"


def allowed_origins(raw: str | None = None) -> set[str]:
    """Normalise the comma-separated ``APP_ORIGINS`` allow-list."""
    value = os.environ.get("APP_ORIGINS", "") if raw is None else raw
    return {
        origin.strip().rstrip("/") for origin in value.split(",") if origin.strip()
    }


def split_state(state: str) -> tuple[str, str]:
    """Split ``<nonce>|<origin>`` into its two parts."""
    nonce, _, origin = state.partition("|")
    return nonce, origin.rstrip("/")


def authorize_url(
    client_id: str,
    redirect_uri: str,
    scope: str,
    state: str,
    origin: str,
) -> str:
    """Build the GitHub authorization URL for ``origin``."""
    params = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "state": f"{state}|{origin}",
        }
    )
    return f"{AUTHORIZE_URL}?{params}"


def exchange_code(
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    code: str,
    *,
    timeout: int = 15,
) -> dict:
    """Exchange an OAuth ``code`` for GitHub's token response."""
    data = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
        }
    ).encode()
    request = urllib.request.Request(
        TOKEN_URL,
        data=data,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)
