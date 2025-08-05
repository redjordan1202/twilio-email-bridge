import logging

from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from dotenv import load_dotenv

from app.endpoints import twilio_webhooks
from app.models import ErrorResponse, ValidationError

logging.basicConfig(level=logging.INFO)

load_dotenv()
app = FastAPI()


@app.exception_handler(HTTPException)
def handle_http_exception(request: Request, exc: HTTPException):
    """
    Handles HTTP exceptions

    Args:
        request: FastAPI request object
        exc: Exception object

    Returns: JSONResponse detailing error that occurred with a status code based on the specific error

    """
    if exc.status_code == 405:
        return JSONResponse(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            content={
                "error_code": 405,
                "description": "Not allowed",
                "message": "Method Not Allowed",
            }
        )

    else:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": exc.status_code,
                "description": "Unknown Error",
                "message": "Unknown Error Occurred",
            }
        )


@app.exception_handler(RequestValidationError)
def handle_request_validation_exception(request: Request, exc: RequestValidationError):
    """
    Handles request validation errors

    Args:
        request: FastAPI request object
        exc: Exception object

    Returns: JSONResponse detailing the validation errors in the data.

    """
    error_response = ValidationError(
        error_code=422,
        validation_errors=[],
        description="Validation Error",
        message="Validation Error. Check for missing fields and try again.",
    )

    for error in exc.errors():
        field_name = error["loc"][-1] if "loc" in error else "Unknown Field"
        validation_error = {
            "field": field_name,
            "message": error["msg"],
            "type": error["type"],
        }
        error_response.validation_errors.append(validation_error)

    return JSONResponse(
        status_code=422,
        content=error_response.model_dump()
    )


app.include_router(twilio_webhooks.router)