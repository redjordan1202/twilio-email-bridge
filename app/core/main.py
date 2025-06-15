from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.endpoints import twilio_webhooks
from app.models import ErrorResponse

app = FastAPI()

@app.exception_handler(HTTPException)
def handle_http_exception(request: Request, exc: HTTPException):
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

app.include_router(twilio_webhooks.router)