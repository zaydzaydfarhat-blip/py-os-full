#!/usr/bin/env python3
"""Serve PY-OS GUI and report applets from the local BusyBox installation."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import shutil
import subprocess


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?", 1)[0] == "/api/applets":
            binary = shutil.which("busybox")
            if not binary:
                payload = {"available": False, "applets": [], "message": "BusyBox was not found in PATH."}
            else:
                try:
                    result = subprocess.run(
                        [binary, "--list"],
                        check=True,
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    applets = sorted(set(result.stdout.splitlines()))
                    payload = {"available": True, "applets": applets, "message": "Detected from your BusyBox binary."}
                except (OSError, subprocess.SubprocessError) as error:
                    payload = {"available": False, "applets": [], "message": f"Could not read BusyBox applets: {error}"}
            data = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
            return
        return super().do_GET()


if __name__ == "__main__":
    print("PY-OS GUI: http://localhost:8000")
    print("BusyBox applet list: detected from the local BusyBox binary when available.")
    ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
