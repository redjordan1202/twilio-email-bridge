from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.responses import JSONResponse

from app.models import TwilioRequest
from app.core.twilio_logic import twilio_background_task

router = APIRouter()

@router.post("/webhooks/twilio")
async def handle_twilio_sms(request: Request, background_tasks: BackgroundTasks = BackgroundTasks):
    data = await request.form()
    try:
        twilio_data = TwilioRequest(**data)
        background_tasks.add_task(twilio_background_task, request, dict(data))
        return JSONResponse(
            status_code=200,
            content={},
        )
    except ValidationError as e:
        raise RequestValidationError(
            errors=e.errors(),
        )
