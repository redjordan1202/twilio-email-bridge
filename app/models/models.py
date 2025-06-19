from typing import List, Optional

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
    NumSegments: str
    To: str
    ForwardedFrom: Optional[str] = None
    MessageStatus: Optional[str] = None
    Body: str
    FromZip: Optional[str] = None
    FromCity: Optional[str] = None
    FromState: Optional[str] = None
    FromCountry: Optional[str] = None
    ToZip: Optional[str] = None
    ToCity: Optional[str] = None
    ToState: Optional[str] = None
    ToCountry: Optional[str] = None
    NumMedia: str
