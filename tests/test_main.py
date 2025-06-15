from fastapi.testclient import TestClient
from app.core.main import app

test_client = TestClient(app)

def test_twilio_webhook_valid_path():
    response = test_client.post("/webhooks/twilio")
    assert response.status_code == 200
    assert response.json() == {}

def test_twilio_webhook_reject_get():
    response = test_client.get("/webhooks/twilio")
    assert response.status_code == 405
