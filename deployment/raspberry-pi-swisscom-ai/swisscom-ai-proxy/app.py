import os

import requests
from flask import Flask, Response, jsonify, request


app = Flask(__name__)

SWISSCOM_API_KEY = os.environ["SWISSCOM_API_KEY"]
SWISSCOM_BASE_URL = os.getenv("SWISSCOM_BASE_URL", "https://code.myai.swisscom.ch/v1").rstrip("/")
SWISSCOM_MODEL = os.getenv("SWISSCOM_MODEL", "qwen3.5-397b-a17b")
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "180"))


@app.get("/health")
def health():
    return jsonify({"ok": True})


@app.get("/v1/models")
def models():
    return jsonify({
        "object": "list",
        "data": [
            {
                "id": SWISSCOM_MODEL,
                "object": "model",
                "owned_by": "swisscom-ai-proxy",
            }
        ],
    })


@app.post("/v1/chat/completions")
def chat_completions():
    payload = request.get_json(force=True, silent=False)
    payload["model"] = SWISSCOM_MODEL

    upstream = requests.post(
        f"{SWISSCOM_BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {SWISSCOM_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    return Response(
        upstream.content,
        status=upstream.status_code,
        content_type=upstream.headers.get("content-type", "application/json"),
    )

