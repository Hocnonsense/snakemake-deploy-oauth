from http.server import BaseHTTPRequestHandler
import os
import sys
from pathlib import Path
import urllib.parse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from oauth_common import allowed_origins, authorize_url


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        state = (query.get("state") or [""])[0]
        origin = (query.get("origin") or [""])[0].rstrip("/")

        if not state or origin not in allowed_origins():
            self._text(400, "Invalid login request.")
            return

        location = authorize_url(
            os.environ["GITHUB_CLIENT_ID"],
            os.environ["GITHUB_CALLBACK_URL"],
            os.environ.get("GITHUB_OAUTH_SCOPE", "read:user public_repo"),
            state,
            origin,
        )
        self.send_response(302)
        self.send_header("Location", location)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def _text(self, code: int, message: str):
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(message.encode())
