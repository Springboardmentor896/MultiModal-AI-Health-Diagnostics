"""
Ollama client utilities (local LLM).
Default server: http://127.0.0.1:11434
"""

from __future__ import annotations

import json
import socket
import urllib.error
import urllib.request


def _post_json(url: str, payload: dict, timeout_seconds: int = 15) -> tuple[dict | None, str | None]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            body = resp.read().decode("utf-8", errors="replace")
        return json.loads(body), None
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode("utf-8", errors="replace")
        except Exception:
            detail = ""
        return None, f"HTTP {getattr(e, 'code', '')} {getattr(e, 'reason', '')}".strip() + (f" - {detail}" if detail else "")
    except (urllib.error.URLError, TimeoutError, socket.timeout) as e:
        return None, str(e) or "Connection error"
    except (ValueError, json.JSONDecodeError) as e:
        return None, f"Invalid JSON response: {e}"


def healthcheck(base_url: str = "http://127.0.0.1:11434", timeout_seconds: int = 5) -> tuple[bool, str]:
    """
    Quick connectivity check using /api/tags.
    Returns (ok, message).
    """
    url = base_url.rstrip("/") + "/api/tags"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            _ = resp.read()
        return True, "Ollama server reachable."
    except Exception as e:
        return False, f"Ollama not reachable at {base_url}. Error: {e}"


def list_models(base_url: str = "http://127.0.0.1:11434", timeout_seconds: int = 10) -> tuple[list[str], str | None]:
    """
    Returns (models, error). Models are names like 'phi3:mini'.
    """
    url = base_url.rstrip("/") + "/api/tags"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            body = resp.read().decode("utf-8", errors="replace")
        obj = json.loads(body)
        models = []
        for m in obj.get("models") or []:
            name = (m or {}).get("name")
            if name:
                models.append(str(name))
        return models, None
    except Exception as e:
        return [], str(e)


def chat(
    messages: list[dict],
    model: str = "phi3:mini",
    base_url: str = "http://127.0.0.1:11434",
    timeout_seconds: int = 30,
) -> tuple[str, str | None]:
    """
    Call Ollama /api/chat.
    Returns (text, error). Error is None on success.
    """
    url = base_url.rstrip("/") + "/api/chat"
    payload = {"model": model, "messages": messages, "stream": False}
    obj, err = _post_json(url, payload, timeout_seconds=timeout_seconds)
    if err:
        return "", err
    msg = (obj or {}).get("message") or {}
    text = (msg.get("content") or "").strip()
    if not text:
        return "", "Empty response from Ollama."
    return text, None

