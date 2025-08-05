import logging
from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette import status
from starlette.responses import JSONResponse

from app.models import TwilioRequest, LogEntry
from app.core.twilio_logic import twilio_background_task, validate_twilio_request, sanitize_data


router = APIRouter()


@router.post("/webhooks/twilio")
async def handle_twilio_sms(request: Request, background_tasks: BackgroundTasks = BackgroundTasks):
    """ Receives and process incoming Twilio SMS webhook requests

    This endpoint receives inbound Twilio SMS messages and sends them to a background task for processing and forwarding.

    Args:
        request: FastAPI Request object.
        background_tasks: FastAPI Background Tasks object.

    Returns:
        JSONResponse: JSONSResponse showing 403 if request is an invalid twilio request, or 200 if request is valid.

    Raises:
        ValidationError: If the incoming Twilio SMS message is structured incorrectly or missing required fields
    """
    data = await request.form()
    data = dict(data)
    headers = dict(request.headers)
    try:
        twilio_data = TwilioRequest(**data)
        if not validate_twilio_request(request, data):
            error_log = LogEntry(
                level="ERROR",
                message="Invalid twilio request",
                service_name="Twilio Webhook",
                trace_id=headers.get("X-Twilio-Trace-ID", "None"),
                context=sanitize_data(data),
            )
            logging.error(error_log)
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"message": "Invalid twilio request"},
            )

        background_tasks.add_task(twilio_background_task, headers, dict(data))
        return JSONResponse(
            status_code=200,
            content={},
        )

    except ValidationError as e:
        raise RequestValidationError(
            errors=e.errors(),
        )
