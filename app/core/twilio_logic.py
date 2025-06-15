from app.models import TwilioRequest
from pydantic import ValidationError

def extract_message_info(twilio_data: dict) -> dict:
    try:
        validated_data = TwilioRequest(**twilio_data)
    except ValidationError as e:
        raise AttributeError from e

    return {}