import os

from app.exceptions.exceptions import MissingCredentialsException
from app.models import TwilioRequest
from pydantic import ValidationError
from twilio.rest import Client


def get_client():
    account_sid = os.environ["TWILIO_ACCOUNT_SID"] if "TWILIO_ACCOUNT_SID" in os.environ else None
    auth_token = os.environ["TWILIO_AUTH_TOKEN"] if "TWILIO_AUTH_TOKEN" in os.environ else None
    if not account_sid or not auth_token:
        raise MissingCredentialsException("Required credentials are missing")


def extract_message_info(twilio_data: dict) -> dict:
    try:
        validated_data = TwilioRequest(**twilio_data)
    except ValidationError as e:
        raise AttributeError from e

    return {}