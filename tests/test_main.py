import pytest
from fastapi.testclient import TestClient
from app.main import app

test_client = TestClient(app)

def test_read_main():
    response = test_client.post("/webhooks/twilio")
    assert response.status_code == 200
    assert response.json() == {}
