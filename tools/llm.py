#!/usr/bin/env python3
# AI-assisted: Claude Code (claude-opus-5-5), reviewed by aalexanderrz
"""The only module that knows the LLM provider (Gemini API, Interactions endpoint).

generate_json(text, schema) sends `text` as the prompt, asks for JSON that follows
`schema`, and returns (parsed_json, model). Changing provider means changing this file.

The key is read from the environment variable LLM_API_KEY, or from a `LLM_API_KEY=...`
line of the local `.env` at the repository root. It is never printed.
The model is MODEL, or the environment variable LLM_MODEL if it is set.

Requests are paced (PAUSE_S between them) and retried with a growing wait on a 429 or
a 5xx answer. Requests are sent with store=false: the provider is asked not to keep
the interaction. Only public NASA text is meant to be sent (free tier data use).

Standard library only. Reference: https://aistudio.google.com/docs/structured-output
and https://aistudio.google.com/api-reference/interactions-api (read 2026-11-15).
"""

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/interactions"
API_REVISION = "2026-05-20"
MODEL = "gemini-3.5-flash-lite"
USER_AGENT = "micro-g-cards/1.0"
PAUSE_S = 6.0
RETRY_WAITS_S = (30, 60, 120, 240)
TIMEOUT_S = 120

_last_call = 0.0


class LLMError(Exception):
    pass


def model_name():
    return os.environ.get("LLM_MODEL") or MODEL


def _api_key():
    key = os.environ.get("LLM_API_KEY")
    if key:
        return key.strip()
    env = ROOT / ".env"
    if env.is_file():
        for line in env.read_text(encoding="utf-8").splitlines():
            name, sep, value = line.partition("=")
            if sep and name.strip() == "LLM_API_KEY":
                value = value.strip().strip('"').strip("'")
                if value:
                    return value
    raise LLMError("LLM_API_KEY is not set (environment or .env)")


def _output_text(interaction):
    """Text of the model_output steps, joined: steps[i].content[j].text."""
    parts = []
    for step in interaction.get("steps") or []:
        if step.get("type") != "model_output":
            continue
        for item in step.get("content") or []:
            if item.get("type") == "text" and isinstance(item.get("text"), str):
                parts.append(item["text"])
    return "".join(parts)


def _post(body, key):
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": key,
            "Api-Revision": API_REVISION,
            "User-Agent": USER_AGENT,
        },
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
        return json.loads(response.read().decode("utf-8"))


def generate_json(text, schema):
    """Send `text`, get back JSON following `schema`. Returns (data, model)."""
    global _last_call
    key = _api_key()
    model = model_name()
    body = {
        "model": model,
        "input": text,
        "store": False,
        "response_format": {
            "type": "text",
            "mime_type": "application/json",
            "schema": schema,
        },
    }
    for attempt in range(len(RETRY_WAITS_S) + 1):
        wait = PAUSE_S - (time.monotonic() - _last_call)
        if wait > 0:
            time.sleep(wait)
        _last_call = time.monotonic()
        try:
            interaction = _post(body, key)
        except urllib.error.HTTPError as err:
            retryable = err.code == 429 or 500 <= err.code < 600
            if not retryable or attempt == len(RETRY_WAITS_S):
                detail = err.read().decode("utf-8", "replace")[:500]
                raise LLMError(f"HTTP {err.code}: {detail}") from None
            retry_after = err.headers.get("Retry-After", "")
            delay = int(retry_after) if retry_after.isdigit() else RETRY_WAITS_S[attempt]
            print(f"llm: HTTP {err.code}, retrying in {delay} s", flush=True)
            time.sleep(delay)
            continue
        status = interaction.get("status")
        if status != "completed":
            raise LLMError(f"interaction status: {status}")
        out = _output_text(interaction)
        try:
            return json.loads(out), interaction.get("model") or model
        except json.JSONDecodeError as err:
            raise LLMError(f"answer is not JSON: {err}") from None
    raise LLMError("unreachable")
