from fastapi import APIRouter, Request, Response
from app.models import TwilioRequest

router = APIRouter()

@router.post("/webhooks/twilio")
def handle_twilio_sms(twilio_request: TwilioRequest):
    return {}