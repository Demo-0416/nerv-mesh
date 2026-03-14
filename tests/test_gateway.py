"""Tests for the gateway HTTP endpoints (health, models, skills)."""

import os

import pytest
from fastapi.testclient import TestClient

from nerv_mesh.config import load_config
from nerv_mesh.gateway import create_app

_has_api_key = bool(os.getenv("CODING_PLAN_API_KEY"))


@pytest.fixture(scope="module")
def client():
    if not _has_api_key:
        pytest.skip("CODING_PLAN_API_KEY not set, skipping gateway integration tests")
    config = load_config()
    app = create_app(config)
    with TestClient(app) as c:
        yield c


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_list_models(client):
    resp = client.get("/api/config/models")
    assert resp.status_code == 200
    data = resp.json()
    assert "default" in data
    assert "model" in data["default"]


def test_list_skills(client):
    resp = client.get("/api/skills")
    assert resp.status_code == 200
    data = resp.json()
    names = {s["name"] for s in data}
    assert "research" in names
