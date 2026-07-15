#!/usr/bin/env python3
"""
EDGAR relay for edgar-ledger.html
---------------------------------
Browsers can't set a User-Agent header from JavaScript, but the SEC
requires one (same reason edgartools makes you call set_identity).
This ~80-line stdlib server fixes that:

  * serves edgar-ledger.html at  http://127.0.0.1:8787/
  * forwards /sec?url=...  to sec.gov with the IDENTITY header below
  * adds CORS headers, so the page works whether you open it from
    this server or double-click the file while the relay runs

Run it from the folder containing edgar-ledger.html:

    python edgar_relay.py

Ctrl+C stops it. No packages needed.
"""
import json
import threading
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

IDENTITY = "email@email.com"   # <-- set_identity: what the SEC sees as your User-Agent
PORT = 8787
ALLOWED_HOSTS = {"sec.gov", "www.sec.gov", "data.sec.gov"}
PAGE = Path(__file__).with_name("edgar-ledger.html")
TIMEOUT = 90  # companyfacts for big filers can be 10 MB+


class Relay(BaseHTTPRequestHandler):
    def log_message(self, *args):  # quiet the default noisy log
        pass

    def _send(self, status, body, ctype="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path in ("/", "/edgar-ledger.html"):
            if not PAGE.exists():
                self._send(404, b'{"error":"edgar-ledger.html not found next to this script"}')
                return
            self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
            return

        if parsed.path == "/sec":
            url = (urllib.parse.parse_qs(parsed.query).get("url") or [""])[0]
            host = urllib.parse.urlparse(url).hostname or ""
            if host not in ALLOWED_HOSTS:
                self._send(400, b'{"error":"only sec.gov URLs are relayed"}')
                return
            req = urllib.request.Request(url, headers={"User-Agent": IDENTITY})
            try:
                with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                    body = r.read()
                    print(f"[relay] {url.split('?')[0]}  {r.status}  {len(body):,} bytes")
                    self._send(r.status, body, r.headers.get("Content-Type", "application/json"))
            except urllib.error.HTTPError as e:            # SEC said no — pass it through visibly
                body = e.read() or json.dumps({"error": f"SEC returned {e.code}"}).encode()
                print(f"[relay] {url.split('?')[0]}  {e.code}")
                self._send(e.code, body)
            except Exception as e:                          # network trouble etc.
                print(f"[relay] {url.split('?')[0]}  FAILED  {e}")
                self._send(502, json.dumps({"error": str(e)}).encode())
            return

        self._send(404, b'{"error":"unknown path"}')


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Relay)
    print(f"EDGAR relay running at http://127.0.0.1:{PORT}/   (Ctrl+C to stop)")
    print(f"Identity declared to SEC: {IDENTITY}")
    threading.Timer(0.5, lambda: webbrowser.open(f"http://127.0.0.1:{PORT}/")).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
