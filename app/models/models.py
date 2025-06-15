from typing import List

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error_code: int
    description: str
    message: str

class ValidationError(BaseModel):
    error_code: int
    validation_errors: List[dict]
    description: str
    message: str

class TwilioRequest(BaseModel):
    SmsSid: str
    SmsStatus: str
    MessageSid: str
    AccountSid: str
    From: str
    ApiVersion: str
    SmsMessageSid: str
    NumSegments: int
    To: str
    ForwardedFrom: str
    MessageStatus: str
    Body: str
    FromZip: str
    FromCity: str
    FromState: str
    FromCountry: str
    ToZip: str
    ToCity: str
    ToState: str
    ToCountry: str
    NumMedia: str
