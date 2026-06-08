"""
SAGCO Serve — organism HTTP server.
Pure Python stdlib. No dependencies. Runs on Termux, Pi, Docker, bare metal.

sagco serve
sagco serve --port 8080
sagco serve --port 8080 --root ~/sagco-world
sagco serve --readonly

Routes:
  GET /                  → organism status HTML dashboard
  GET /api/status        → JSON organism status
  GET /api/palace        → JSON memory palace index
  GET /api/health        → wafer truth test result
  GET /files/<path>      → serve files from organism root
  GET /palace.json       → shortcut to memory palace
"""

from __future__ import annotations

import html
import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse


# ── Request handler ───────────────────────────────────────────────────────

class SAGCOHandler(BaseHTTPRequestHandler):
    organism_root: Path = Path(".")
    start_time: float = time.time()
    readonly: bool = True

    def log_message(self, fmt, *args):
        ts = time.strftime("%H:%M:%S")
        print(f"  [{ts}] {fmt % args}")

    def do_GET(self):
        parsed = urlparse(self.path)
        path   = parsed.path

        try:
            if path in ("/", ""):
                self._serve_dashboard()
            elif path in ("/api/status",):
                self._serve_json(self._organism_status())
            elif path in ("/api/palace", "/palace.json"):
                self._serve_palace()
            elif path in ("/api/health",):
                self._serve_health()
            elif path.startswith("/files"):
                self._serve_file(path[6:].lstrip("/"))
            else:
                self._404(path)
        except Exception as e:
            self._500(str(e))

    # ── Route handlers ────────────────────────────────────────────────────

    def _serve_dashboard(self):
        status = self._organism_status()
        nodes_html = ""
        for name, node in status.get("nodes", {}).items():
            icon  = "●" if node.get("online") else "○"
            color = "#4caf50" if node.get("online") else "#666"
            counts = "  ".join(
                f"{k}:{v}" for k, v in node.get("component_counts", {}).items()
            )
            nodes_html += f"""
            <tr>
              <td style="color:{color}">{icon} {html.escape(name)}</td>
              <td>{html.escape(node.get('role', ''))}</td>
              <td style="font-size:0.85em;color:#aaa">{html.escape(counts)}</td>
            </tr>"""

        summary = status.get("summary", {})
        page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>SAGCO Organism Status</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: #0d0d0d; color: #e0e0e0; font-family: monospace; padding: 1.5rem; }}
    h1   {{ color: #ff6b35; letter-spacing: 2px; margin-bottom: 0.5rem; }}
    .sub {{ color: #666; font-size: 0.85em; margin-bottom: 2rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
    .card {{ background: #1a1a1a; border: 1px solid #333; border-radius: 6px; padding: 1rem; }}
    .card .num {{ font-size: 2rem; color: #ff6b35; }}
    .card .lbl {{ font-size: 0.8em; color: #888; margin-top: 0.25rem; }}
    table {{ width: 100%; border-collapse: collapse; margin-bottom: 2rem; }}
    th    {{ text-align: left; color: #666; font-size: 0.8em; border-bottom: 1px solid #333; padding: 0.5rem 0; }}
    td    {{ padding: 0.4rem 0.5rem; font-size: 0.9em; border-bottom: 1px solid #1a1a1a; }}
    .links a {{ color: #ff6b35; text-decoration: none; margin-right: 1rem; }}
    .links a:hover {{ text-decoration: underline; }}
    .status {{ color: #4caf50; font-weight: bold; }}
  </style>
</head>
<body>
  <h1>SAGCO</h1>
  <p class="sub">Sovereignty Architecture Graph Command Orchestrator &nbsp;·&nbsp; v0.1.0</p>

  <div class="grid">
    <div class="card"><div class="num">{summary.get('total_entries', 0)}</div><div class="lbl">indexed entries</div></div>
    <div class="card"><div class="num">{summary.get('nodes_online', 0)}</div><div class="lbl">nodes online</div></div>
    <div class="card"><div class="num">{summary.get('total_size_kb', 0):.1f} KB</div><div class="lbl">indexed size</div></div>
    <div class="card"><div class="num">{_uptime(self.start_time)}</div><div class="lbl">server uptime</div></div>
  </div>

  <table>
    <tr><th>Node</th><th>Role</th><th>Components</th></tr>
    {nodes_html}
  </table>

  <table>
    <tr><th>Kind</th><th>Count</th></tr>
    {''.join(f"<tr><td>{html.escape(k)}</td><td>{v}</td></tr>" for k, v in summary.get('kinds', {}).items())}
  </table>

  <div class="links">
    <a href="/api/status">api/status</a>
    <a href="/api/palace">api/palace</a>
    <a href="/api/health">api/health</a>
    <a href="/files/">files/</a>
  </div>

  <br><p style="color:#4caf50">STATUS: ORGANISM_SERVING</p>
</body>
</html>"""
        self._send(200, page.encode(), "text/html; charset=utf-8")

    def _serve_json(self, obj: Any):
        data = json.dumps(obj, indent=2).encode()
        self._send(200, data, "application/json")

    def _serve_palace(self):
        palace_path = self.organism_root / "palace.json"
        if palace_path.exists():
            data = palace_path.read_bytes()
            self._send(200, data, "application/json")
        else:
            # Run a quick scan on-the-fly
            try:
                sys.path.insert(0, str(self.organism_root.parent))
                from sagco_true.worlds.palace import scan
                idx = scan(self.organism_root)
                data = json.dumps(idx.to_dict(), indent=2).encode()
                self._send(200, data, "application/json")
            except Exception as e:
                self._serve_json({"error": str(e), "note": "palace.json not found and scan failed"})

    def _serve_health(self):
        try:
            sys.path.insert(0, str(self.organism_root.parent))
            from sagco_true.wafers.runner import run_truth_test
            result = run_truth_test()
            self._serve_json(result)
        except Exception as e:
            self._serve_json({"error": str(e), "status": "WAFER_RUNNER_UNAVAILABLE"})

    def _serve_file(self, rel_path: str):
        safe = unquote(rel_path).lstrip("/").replace("..", "")
        full = self.organism_root / safe

        if full.is_dir():
            # Directory listing
            try:
                entries = sorted(full.iterdir(), key=lambda p: (p.is_file(), p.name))
            except PermissionError:
                self._403()
                return
            items = ""
            if rel_path:
                parent = str(Path(rel_path).parent)
                items += f'<li><a href="/files/{parent}">../</a></li>'
            for e in entries:
                icon = "📁" if e.is_dir() else "📄"
                name = e.name + ("/" if e.is_dir() else "")
                link = f"/files/{rel_path.rstrip('/')}/{e.name}".replace("//", "/")
                size = ""
                if e.is_file():
                    try:
                        size = f" ({e.stat().st_size} B)"
                    except Exception:
                        pass
                items += f'<li>{icon} <a href="{html.escape(link)}">{html.escape(name)}</a>{size}</li>'

            page = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>body{{background:#0d0d0d;color:#e0e0e0;font-family:monospace;padding:1rem}}
a{{color:#ff6b35}}li{{padding:0.2rem 0}}</style></head>
<body><h3>/{html.escape(rel_path)}</h3><ul>{items}</ul>
<p><a href="/">← organism status</a></p></body></html>"""
            self._send(200, page.encode(), "text/html; charset=utf-8")
            return

        if not full.exists() or not full.is_file():
            self._404(rel_path)
            return

        # File: detect MIME, stream
        ext = full.suffix.lower()
        mime_map = {
            ".json": "application/json",
            ".sagco": "text/plain; charset=utf-8",
            ".sagcob": "application/octet-stream",
            ".yaml": "text/plain; charset=utf-8",
            ".yml": "text/plain; charset=utf-8",
            ".md": "text/plain; charset=utf-8",
            ".txt": "text/plain; charset=utf-8",
            ".py": "text/plain; charset=utf-8",
            ".rs": "text/plain; charset=utf-8",
            ".sh": "text/plain; charset=utf-8",
            ".html": "text/html; charset=utf-8",
            ".csv": "text/csv",
            ".log": "text/plain; charset=utf-8",
        }
        mime = mime_map.get(ext, "application/octet-stream")
        try:
            data = full.read_bytes()
            self._send(200, data, mime)
        except PermissionError:
            self._403()

    # ── Data helpers ──────────────────────────────────────────────────────

    def _organism_status(self) -> dict:
        palace_path = self.organism_root / "palace.json"
        if palace_path.exists():
            try:
                return json.loads(palace_path.read_text())
            except Exception:
                pass
        return {
            "palace": {"organism": "SAGCO", "version": "0.1.0"},
            "nodes": {},
            "summary": {"total_entries": 0, "nodes_online": 0, "total_size_kb": 0, "kinds": {}},
        }

    # ── HTTP helpers ──────────────────────────────────────────────────────

    def _send(self, code: int, body: bytes, content_type: str):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _404(self, path: str = ""):
        body = json.dumps({"error": "not found", "path": path}).encode()
        self._send(404, body, "application/json")

    def _403(self):
        body = json.dumps({"error": "forbidden"}).encode()
        self._send(403, body, "application/json")

    def _500(self, msg: str):
        body = json.dumps({"error": "internal error", "detail": msg}).encode()
        self._send(500, body, "application/json")


# ── Server startup ────────────────────────────────────────────────────────

def _uptime(start: float) -> str:
    s = int(time.time() - start)
    if s < 60:   return f"{s}s"
    if s < 3600: return f"{s//60}m"
    return f"{s//3600}h"


def serve(
    organism_root: str | Path | None = None,
    port: int = 8080,
    host: str = "0.0.0.0",
    readonly: bool = True,
) -> None:
    if organism_root is None:
        organism_root = Path(__file__).parent.parent.resolve()
    organism_root = Path(organism_root).resolve()

    SAGCOHandler.organism_root = organism_root
    SAGCOHandler.start_time    = time.time()
    SAGCOHandler.readonly      = readonly

    server = HTTPServer((host, port), SAGCOHandler)

    # Try to detect LAN IP for display
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        lan_ip = s.getsockname()[0]
        s.close()
    except Exception:
        lan_ip = "127.0.0.1"

    print(f"\n  SAGCO Organism Server")
    print(f"  Root: {organism_root}")
    print(f"\n  Local :  http://localhost:{port}")
    print(f"  LAN   :  http://{lan_ip}:{port}")
    print(f"\n  Routes:")
    print(f"    GET /             → organism dashboard")
    print(f"    GET /api/status   → JSON status")
    print(f"    GET /api/palace   → memory palace index")
    print(f"    GET /api/health   → wafer truth tests")
    print(f"    GET /files/...    → browse organism files")
    print(f"\n  Ctrl-C to stop\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        server.server_close()
