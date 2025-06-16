from fastapi.testclient import TestClient
from app.core.main import app
import json

test_client = TestClient(app)

dummy_message = {
    "SmsSid": "SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "SmsStatus": "received",
    "MessageSid": "SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "AccountSid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "From": "+11234567890",
    "ApiVersion": '2010-04-01',
    "SmsMessageSid": "SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "NumSegments": "1",
    "To": "+10987654321",
    "ForwardedFrom": "",
    "MessageStatus": "received",
    "Body": "Hello World",
    "NumMedia": "0"
}

def test_twilio_webhook_handles_valid_request():
    response = test_client.post("/webhooks/twilio", data=dummy_message)
    print(response.request.content)
    assert response.status_code == 200
    assert response.json() == {}

def test_twilio_webhook_reject_get():
    response = test_client.get("/webhooks/twilio")
    assert response.status_code == 405
    assert response.json() == {
        "error_code": 405,
        "description": "Not allowed",
        "message": "Method Not Allowed",
    }

def test_twilio_webhook_raises_error_missing_body_in_form():
    form_data = {
        'SmsSid': 'SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'SmsStatus': 'received',
        'MessageSid': 'SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'AccountSid': 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'From': '+11234567890',
        'ApiVersion': '2010-04-01',
        'SmsMessageSid': 'SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        'NumSegments': '1',
        'To': '+10987654321',
        'ForwardedFrom': '',
        'MessageStatus': 'received',
        # 'Body': 'Hello, World!', # excluding body for test
        'FromZip': '12345',
        'FromCity': 'Townsville',
        'FromState': 'CA',
        'FromCountry': 'US',
        'ToZip': '4321',
        'ToCity': 'Citysberg',
        'ToState': 'CA',
        'ToCountry': 'US',
        'NumMedia': '0',
    }
    response = test_client.post("/webhooks/twilio", data=form_data)

    assert response.status_code == 422
    assert "Validation Error" in response.json()["description"]
    assert len(response.json()["validation_errors"]) > 0
    assert response.json()["validation_errors"][0]["field"] == "body"
