"""
Automated unit tests for Vercel serverless API handlers (api/index.py).
"""

import io
import json
import pytest
from api.index import handler, simulate_qiskit_circuit, generate_qollab_notebook_json


class MockSocket:
    def __init__(self, data: bytes):
        self.rfile = io.BytesIO(data)
        self.wfile = io.BytesIO()

    def makefile(self, mode, *args, **kwargs):
        if "r" in mode:
            return self.rfile
        return self.wfile

    def sendall(self, b):
        self.wfile.write(b)


def send_mock_request(method: str, path: str, body: bytes = b"", headers: dict = None):
    headers = headers or {}
    req_lines = [f"{method} {path} HTTP/1.1", f"Host: localhost", f"Content-Length: {len(body)}"]
    for k, v in headers.items():
        req_lines.append(f"{k}: {v}")
    raw_req = "\r\n".join(req_lines) + "\r\n\r\n"
    sock = MockSocket(raw_req.encode("utf-8") + body)
    h = handler(sock, ("127.0.0.1", 12345), None)
    sock.wfile.seek(0)
    raw_resp = sock.wfile.read().decode("utf-8", errors="replace")
    
    parts = raw_resp.split("\r\n\r\n", 1)
    header_part = parts[0]
    body_part = parts[1] if len(parts) > 1 else ""
    status_line = header_part.splitlines()[0]
    status_code = int(status_line.split()[1])
    return status_code, body_part


def test_api_health_endpoint():
    status, body = send_mock_request("GET", "/api/health")
    assert status == 200
    data = json.loads(body)
    assert data["status"] == "healthy"
    assert "qpu_target" in data


def test_api_qollab_notebook_endpoint():
    status, body = send_mock_request("GET", "/api/qollab")
    assert status == 200
    data = json.loads(body)
    assert "cells" in data
    assert data["nbformat"] == 4


def test_api_qollab_py_endpoint():
    status, body = send_mock_request("GET", "/api/qollab?format=py")
    assert status == 200
    assert "def main(" in body
    assert "qollab.xyz" in body
    assert "backend.run" in body


def test_api_qollab_json_endpoint():
    status, body = send_mock_request("GET", "/api/qollab?format=json")
    assert status == 200
    data = json.loads(body)
    assert data["platform"] == "qollab.xyz"
    assert data["requires_api_key"] is False
    assert "main_py" in data



def test_api_simulate_tuples_and_dicts():
    # 1. Tuples format
    body1 = json.dumps({
        "melody": [[60, 1.0], [62, 1.0], [64, 1.0]],
        "key_root": "C",
        "key_mode": "major"
    }).encode("utf-8")
    status1, resp1 = send_mock_request("POST", "/api/simulate", body1, {"Content-Type": "application/json"})
    assert status1 == 200
    d1 = json.loads(resp1)
    assert len(d1["voices"]) == 3
    assert d1["chsh_s"] >= 2.0

    # 2. Dicts format (regression test for I2)
    body2 = json.dumps({
        "melody": [{"pitch": 60, "duration": 1.0}, {"pitch": 64, "duration": 1.0}],
        "key_root": "C",
        "key_mode": "major"
    }).encode("utf-8")
    status2, resp2 = send_mock_request("POST", "/api/simulate", body2, {"Content-Type": "application/json"})
    assert status2 == 200
    d2 = json.loads(resp2)
    assert len(d2["voices"]) == 2


def test_api_ionq_endpoint():
    body = json.dumps({
        "alpha": 0.785,
        "beta": 0.392,
        "shots": 1000
    }).encode("utf-8")
    status, resp = send_mock_request("POST", "/api/ionq", body, {"Content-Type": "application/json"})
    assert status == 200
    data = json.loads(resp)
    assert "qpu_counts" in data
    assert data["backend"] == "ionq_qpu.aria-1"


def test_path_traversal_blocked():
    # Security test for C1
    status, body = send_mock_request("GET", "/../requirements.txt")
    assert status == 404
    assert body == "Not found"
