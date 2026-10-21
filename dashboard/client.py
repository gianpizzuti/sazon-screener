"""Thin HTTP client: the dashboard talks to the same API an ATS or a chat widget would."""

from __future__ import annotations

import os

import httpx
import streamlit as st

API_URL = os.getenv("SCREENER_API_URL", "http://localhost:8000")
_client = httpx.Client(base_url=API_URL, timeout=60.0)


class ApiUnavailable(Exception):
    pass


def _call(method: str, path: str, **kwargs):
    try:
        response = _client.request(method, path, **kwargs)
    except httpx.TransportError as exc:
        raise ApiUnavailable(f"The API at {API_URL} is not reachable. Start everything with `make run`.") from exc
    response.raise_for_status()
    return response.json()


def candidates(**filters) -> list[dict]:
    return _call("GET", "/candidates", params={k: v for k, v in filters.items() if v})


def candidate(conversation_id: str) -> dict:
    return _call("GET", f"/candidates/{conversation_id}")


def review(conversation_id: str, status: str, note: str, by: str) -> dict:
    return _call("PUT", f"/candidates/{conversation_id}/review", json={"status": status, "note": note, "by": by})


def erase(conversation_id: str) -> None:
    try:
        response = _client.delete(f"/candidates/{conversation_id}")
    except httpx.TransportError as exc:
        raise ApiUnavailable(f"The API at {API_URL} is not reachable.") from exc
    response.raise_for_status()


def regenerate_summary(conversation_id: str) -> dict:
    return _call("POST", f"/candidates/{conversation_id}/summary")


def server_now() -> str:
    return _call("GET", "/health")["now"]


def demo_clock() -> dict | None:
    """The simulated clock, or None when demo tools are disabled."""
    try:
        return _call("GET", "/demo/clock")
    except httpx.HTTPStatusError:
        return None


def advance(hours: float) -> dict:
    return _call("POST", "/demo/advance", json={"hours": hours})


def analytics() -> dict:
    return _call("GET", "/analytics")


def start_conversation(language: str | None) -> dict:
    return _call("POST", "/conversations", json={"channel": "web", "language": language})


def send_message(conversation_id: str, text: str) -> dict:
    return _call("POST", f"/conversations/{conversation_id}/messages", params={"debug": "true"}, json={"text": text})


def guarded(fn):
    """Run a page body; show a helpful message instead of a stack trace when the API is down."""
    try:
        fn()
    except ApiUnavailable as exc:
        st.error(str(exc), icon=":material/cloud_off:")
    except httpx.HTTPStatusError as exc:
        st.error(f"API error {exc.response.status_code}: {exc.response.text[:300]}", icon=":material/error:")
