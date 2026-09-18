#!/usr/bin/env python3
import os
import re
import requests
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# --- ARCHITEKTONICKÁ KONFIGURACE ---
BACKEND_URL = "http://127.0.0.1:5000"
MAX_BLOB_SIZE = 5 * 1024 * 1024
HEX_HASH_REGEX = re.compile(r"^[A-F0-9]{64,128}$", re.IGNORECASE)
ALLOWED_COMPANY_ORIGIN = "https://app.inloopid.com"

@app.after_request
def apply_security_headers(response):
    """Aplikace OWASP bezpečnostních standardů."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none';"
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    return response

@app.route("/api/v1/audit/verify", methods=["POST", "OPTIONS"])
def audit_verify_gateway():
    """Veřejná vrstva pro auditní orgány."""
    if request.method == "OPTIONS":
        resp = Response()
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return resp

    if request.content_length and request.content_length > 4096:
        return jsonify({"error": "Payload Too Large"}), 413

    data = request.get_json(silent=True)
    if not data or "hash" not in data:
        return jsonify({"error": "Bad Request: Missing hash parameter"}), 400

    target_hash = data.get("hash", "")
    if not HEX_HASH_REGEX.match(target_hash):
        return jsonify({"error": "Invalid payload format. Expected hex string."}), 400

    try:
        # Tunelování validovaného požadavku na interní backend
        backend_resp = requests.post(f"{BACKEND_URL}/api/v1/audit/verify", json=data, timeout=5)
        return Response(backend_resp.content, backend_resp.status_code, backend_resp.headers.items())
    except requests.exceptions.RequestException:
        return jsonify({"error": "Internal backend service unavailable"}), 503

@app.route("/api/v1/blobs/storage", methods=["POST", "OPTIONS"])
def blobs_storage_gateway():
    """Kritická infrastruktura pro šifrované bloby (Zero-Knowledge)."""
    origin = request.headers.get("Origin", "")
    
    if request.method == "OPTIONS":
        resp = Response()
        if origin == ALLOWED_COMPANY_ORIGIN:
            resp.headers["Access-Control-Allow-Origin"] = ALLOWED_COMPANY_ORIGIN
            resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
            resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return resp

    if origin != ALLOWED_COMPANY_ORIGIN and os.environ.get("ENV") == "production":
        return jsonify({"error": "Unauthorized origin domain"}), 403

    if request.content_length and request.content_length > MAX_BLOB_SIZE:
        return jsonify({"error": "Payload Too Large."}), 413

    content_type = request.headers.get("Content-Type", "")
    if "application/octet-stream" not in content_type and "application/json" not in content_type:
        return jsonify({"error": "Unsupported Media Type."}), 415

    try:
        # Streamování binárních dat na interní backend bez nutnosti jejich dekódování na bráně
        backend_resp = requests.post(
            f"{BACKEND_URL}/api/v1/blobs/storage",
            data=request.stream,
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            timeout=30
        )
        return Response(backend_resp.content, backend_resp.status_code, backend_resp.headers.items())
    except requests.exceptions.RequestException:
        return jsonify({"error": "Internal backend service unavailable"}), 503

if __name__ == "__main__":
    print("[Gateway] Startuji Security Hardened API Gateway na portu 8080...")
    app.run(host="0.0.0.0", port=8080, debug=False)
