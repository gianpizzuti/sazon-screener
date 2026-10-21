"""API: channel and recruiter endpoints, wired to an offline engine."""

import pytest
from fastapi.testclient import TestClient

from conftest import analysis, start_expr
from screener.api.app import create_app


@pytest.fixture
def client_for(make_engine):
    def _client(script):
        engine = make_engine(script)
        return TestClient(create_app(engine)), engine

    return _client


FIRST = "Soy Ana López, tengo carnet y reparto en Getafe"
TEXTS = [FIRST, "media jornada", "tardes", "nunca", "ya", "sí"]


def full_screening():
    return [
        analysis(FIRST, full_name="Ana López", drivers_license="yes", location_text="Getafe"),
        analysis("media jornada", availability=["part_time"]),
        analysis("tardes", schedule=["afternoon"]),
        analysis("nunca", experience_months=0),
        analysis("ya", start_date=start_expr("immediate")),
        analysis("sí", intents=("affirm",)),
    ]


def run(client, cid, texts):
    for text in texts:
        response = client.post(f"/conversations/{cid}/messages", json={"text": text})
        assert response.status_code == 200
    return response.json()


def test_full_conversation_over_http(client_for):
    client, _ = client_for(full_screening())
    with client:
        start = client.post("/conversations", json={"channel": "web"}).json()
        assert "Sofía" in start["messages"][0]["text"]
        last = run(client, start["conversation_id"], TEXTS)
        assert last["stage"] == "qualified" and last["completed"]
        assert last["analysis"] is None  # the model's internals are never sent to candidates by default


def test_debug_flag_exposes_the_analysis(client_for):
    client, _ = client_for([analysis("sí", intents=("affirm",))])
    with client:
        cid = client.post("/conversations", json={}).json()["conversation_id"]
        body = client.post(f"/conversations/{cid}/messages?debug=true", json={"text": "sí"}).json()
        assert body["analysis"]["intents"] == ["affirm"]


def test_unknown_conversation_is_404(client_for):
    client, _ = client_for([])
    with client:
        assert client.post("/conversations/nope/messages", json={"text": "hola"}).status_code == 404
        assert client.get("/candidates/nope").status_code == 404


def test_empty_message_is_rejected(client_for):
    client, _ = client_for([])
    with client:
        cid = client.post("/conversations", json={}).json()["conversation_id"]
        assert client.post(f"/conversations/{cid}/messages", json={"text": ""}).status_code == 422


def test_recruiter_queue_detail_and_analytics(client_for):
    client, _ = client_for(full_screening())
    with client:
        cid = client.post("/conversations", json={}).json()["conversation_id"]
        run(client, cid, TEXTS)
        queue = client.get("/candidates", params={"status": "qualified"}).json()
        assert [r["name"] for r in queue] == ["Ana López"] and queue[0]["city"] == "Madrid"
        detail = client.get(f"/candidates/{cid}").json()
        assert detail["data"]["zone"] == "Getafe" and len(detail["transcript"]) == 13
        stats = client.get("/analytics").json()
        assert stats["totals"]["qualified"] == 1 and stats["qualified_rate"] == 1.0


def test_overriding_the_bot_is_audited(client_for):
    client, engine = client_for([analysis("sí", intents=("affirm",)), analysis("no tengo", drivers_license="no")])
    with client:
        cid = client.post("/conversations", json={}).json()["conversation_id"]
        run(client, cid, ["sí", "no tengo"])
        response = client.put(f"/candidates/{cid}/review", json={"status": "interview", "note": "Uses an e-bike, client accepts it", "by": "marta"})
        assert response.status_code == 200 and response.json()["status"] == "interview"
        types = [e.type for e in engine.repo.events(cid)]
        assert "human_override" in types and "review_status_changed" in types
        assert client.get("/analytics").json()["human_overrides"] == 1
        assert client.put(f"/candidates/{cid}/review", json={"status": "maybe"}).status_code == 422


def test_silent_candidates_become_abandoned_and_show_where_they_stopped(make_engine):
    from datetime import datetime, timedelta

    from screener.analytics import compute
    from screener.views import build_rows

    engine = make_engine([analysis("sí", intents=("affirm",)), analysis("Ana López", full_name="Ana López")])
    cid = engine.start().conversation_id
    engine.handle(cid, "sí")
    engine.handle(cid, "Ana López")  # now asked for the licence, then silence
    later = datetime(2026, 10, 20, 10, 0) + timedelta(hours=3)
    assert build_rows(engine.repo, now=later)[0].status == "abandoned"
    assert build_rows(engine.repo, now=datetime(2026, 10, 20, 10, 30))[0].status == "in_progress"
    assert compute(engine.repo, now=later).drop_off == {"License": 1}


def test_candidate_data_can_be_erased(client_for):
    client, engine = client_for([analysis("sí", intents=("affirm",))])
    with client:
        cid = client.post("/conversations", json={}).json()["conversation_id"]
        client.post(f"/conversations/{cid}/messages", json={"text": "sí"})
        assert client.delete(f"/candidates/{cid}").status_code == 204
        assert client.get(f"/candidates/{cid}").status_code == 404
        assert engine.repo.events(cid) == [] and engine.repo.messages(cid) == []
        assert client.delete(f"/candidates/{cid}").status_code == 404
