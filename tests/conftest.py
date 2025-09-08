import pytest
from unittest.mock import patch


@pytest.fixture(autouse=True)
def mock_environment_variables():
    with patch.dict('os.environ', {
        "TWILIO_AUTH_TOKEN": "fake_token",
        "DELEGATED_USER_EMAIL": "fake@example.com",
        "FROM_ADDRESS": "fake@example.com",
        "PROJECT_ID": "fake-project",
        "SECRET_NAME": "fake-secret",
        "TWILIO_ACCOUNT_SID": "fake_sid",
        "MY_EMAIL": "fake@example.com"
    }):
        yield
