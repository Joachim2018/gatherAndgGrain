import json
import re
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import urlparse


ROOT = Path(__file__).parent.resolve()
DATA_DIR = ROOT / "data"
PORT = 3000
WRITE_LOCK = Lock()
SUBMISSIONS = {
    "/api/reservations": ("reservations.json", ("name", "email", "date", "time", "guests"), ("notes",)),
    "/api/messages": ("messages.json", ("name", "email", "subject", "message"), ()),
}


class RestaurantHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if urlparse(self.path).path.startswith("/data/"):
            self.send_error(404)
            return
        super().do_GET()

    def do_POST(self):
        route = urlparse(self.path).path
        if route not in SUBMISSIONS:
            self.send_error(404)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 20_000:
                raise ValueError("Request is too large or empty.")
            payload = json.loads(self.rfile.read(length))
            file_name, required_fields, optional_fields = SUBMISSIONS[route]
            record = {}
            for field in required_fields:
                value = payload.get(field)
                if not isinstance(value, str) or not value.strip():
                    self._send_json(400, {"error": f"Please provide {field}."})
                    return
                record[field] = value.strip()
            for field in optional_fields:
                value = payload.get(field, "")
                if isinstance(value, str) and value.strip():
                    record[field] = value.strip()
            if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", record["email"]):
                self._send_json(400, {"error": "Please enter a valid email address."})
                return

            record["submittedAt"] = datetime.now(timezone.utc).isoformat()
            file_path = DATA_DIR / file_name
            with WRITE_LOCK:
                records = json.loads(file_path.read_text(encoding="utf-8"))
                records.append(record)
                file_path.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
            self._send_json(201, {"saved": True})
        except (ValueError, TypeError, json.JSONDecodeError, OSError):
            self._send_json(400, {"error": "We couldn't save that submission. Please try again."})

    def _send_json(self, status, body):
        content = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format_string, *args):
        print(f"{self.address_string()} - {format_string % args}")


if __name__ == "__main__":
    DATA_DIR.mkdir(exist_ok=True)
    for file_name in ("reservations.json", "messages.json"):
        file_path = DATA_DIR / file_name
        if not file_path.exists():
            file_path.write_text("[]\n", encoding="utf-8")
    server = ThreadingHTTPServer(("127.0.0.1", PORT), RestaurantHandler)
    print(f"Gather & Grain is running at http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()