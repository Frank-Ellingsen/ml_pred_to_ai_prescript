"""Lightweight zero-dependency HTTP server and SQLite data sync bridge for Project Finance AI."""

import http.server
import json
import socketserver
import sqlite3
import webbrowser
from pathlib import Path
from typing import Any

PORT = 8000
DB_PATH = Path("data/processed/finance.db")
EXPORT_PATH = Path("data/processed/db_export.json")


def dump_sqlite_to_dict() -> dict[str, list[dict[str, Any]]]:
    """Query SQLite tables and return as dictionary."""
    if not DB_PATH.exists():
        return {}

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    tables = ["actuals", "budgets", "forecasts", "documents", "feedback"]
    payload: dict[str, list[dict[str, Any]]] = {}

    for table in tables:
        try:
            rows = conn.execute(f"SELECT * FROM {table}").fetchall()
            payload[table] = [dict(row) for row in rows]
        except Exception:
            payload[table] = []

    conn.close()
    return payload


class FinanceAIRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler serving index.html and providing /api/sync-db."""

    def do_GET(self) -> None:
        if self.path in ("/", "/index", "/dashboard"):
            self.path = "/index.html"
            return super().do_GET()

        if self.path.startswith("/api/sync-db"):
            data = dump_sqlite_to_dict()
            # Also keep db_export.json fresh
            try:
                EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
                with open(EXPORT_PATH, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
            except Exception:
                pass

            body = json.dumps(data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        return super().do_GET()


def main() -> None:
    """Start local development server and open browser."""
    # Ensure export file is up to date on start
    data = dump_sqlite_to_dict()
    if data:
        EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(EXPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    handler = FinanceAIRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"Project Finance AI Server running at: {url}")
        print(f"Connected to SQLite database: {DB_PATH.resolve()}")
        print("Serving index.html with live /api/sync-db endpoint. Press Ctrl+C to stop.")
        try:
            webbrowser.open(url)
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")


if __name__ == "__main__":
    main()
