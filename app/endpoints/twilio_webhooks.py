from fastapi import APIRouter, Request, Response, Depends
from app.models import TwilioRequest

router = APIRouter()

@router.post("/webhooks/twilio")
def handle_twilio_sms(twilio_request: TwilioRequest = Depends()):
    pass