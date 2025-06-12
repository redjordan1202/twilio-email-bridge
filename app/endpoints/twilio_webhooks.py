from fastapi import APIRouter, Request, Response

router = APIRouter()

@router.post("/webhooks/twilio")
def handle_twilio_sms(request: Request, response: Response):
    return {}