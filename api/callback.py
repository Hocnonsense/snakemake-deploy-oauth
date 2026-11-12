from http.server import BaseHTTPRequestHandler
import html
import json
import os
import sys
from pathlib import Path
import urllib.parse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from oauth_common import allowed_origins, exchange_code, split_state


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        code = (query.get("code") or [""])[0]
        state = (query.get("state") or [""])[0]
        nonce, origin = split_state(state)

        if not code or not nonce or origin not in allowed_origins():
            self._error(400, "Invalid OAuth state.")
            return

        try:
            payload = exchange_code(
                os.environ["GITHUB_CLIENT_ID"],
                os.environ["GITHUB_CLIENT_SECRET"],
                os.environ["GITHUB_CALLBACK_URL"],
                code,
            )
        except Exception:  # noqa: BLE001 - reported to the popup
            self._error(502, "GitHub did not answer.")
            return

        token = payload.get("access_token")
        if not token:
            message = payload.get("error_description") or "No access token."
            self._error(400, html.escape(message))
            return

        message = json.dumps({"token": token, "state": nonce})
        page = f"""<!doctype html>
<html>
<head><meta charset="utf-8"><title>Signed in</title></head>
<body>
<script>
  const target = {json.dumps(origin)};
  const message = {message};
  if (window.opener) {{
    window.opener.postMessage(message, target);
    window.close();
  }} else {{
    document.body.textContent = "Login completed. You can close this tab.";
  }}
</script>
</body>
</html>"""
        self._html(200, page)

    def _error(self, code: int, message: str):
        self._html(code, f"<!doctype html><p>{message}</p>")

    def _html(self, code: int, page: str):
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(page.encode())
