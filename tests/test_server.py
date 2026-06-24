from fastapi.testclient import TestClient
from server.app import api

def test_get_v1_returns_nodes():
    client = TestClient(api)
    r = client.get("/views/V1")
    assert r.status_code == 200
    assert any(n["type"] == "claim" for n in r.json())

def test_unknown_view_404():
    assert TestClient(api).get("/views/V9").status_code == 404
