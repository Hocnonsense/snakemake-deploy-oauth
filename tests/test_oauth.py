"""Pure helpers for the OAuth endpoints."""

import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from oauth_common import allowed_origins, authorize_url, split_state


def test_allowed_origins_normalizes_entries():
    assert allowed_origins(
        "https://example.github.io/, http://localhost:8000 ,"
    ) == {"https://example.github.io", "http://localhost:8000"}


def test_split_state_returns_nonce_and_origin():
    assert split_state("abc|https://example.github.io/") == (
        "abc",
        "https://example.github.io",
    )


def test_authorize_url_keeps_state_and_origin():
    url = authorize_url(
        "client",
        "https://oauth.example/api/callback",
        "read:user public_repo",
        "nonce",
        "https://example.github.io",
    )
    query = parse_qs(urlparse(url).query)

    assert query["client_id"] == ["client"]
    assert query["redirect_uri"] == ["https://oauth.example/api/callback"]
    assert query["state"] == ["nonce|https://example.github.io"]
