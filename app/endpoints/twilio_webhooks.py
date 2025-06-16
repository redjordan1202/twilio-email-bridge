from fastapi import APIRouter, Request, Response, Depends
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.responses import JSONResponse

from app.models import TwilioRequest

router = APIRouter()

@router.post("/webhooks/twilio")
async def handle_twilio_sms(request: Request):
    data = await request.form()
    try:
        twilio_data = TwilioRequest(**data)
        return JSONResponse(
            status_code=200,
            content={},
        )
    except ValidationError as e:
        raise RequestValidationError(
            errors=e.errors(),
        )
