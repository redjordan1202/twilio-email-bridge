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
    NumSegments: int
    To: str
    ForwardedFrom: str
    MessageStatus: str
    Body: str
    FromZip: Optional[str]
    FromCity: Optional[str]
    FromState: Optional[str]
    FromCountry: Optional[str]
    ToZip: Optional[str]
    ToCity: Optional[str]
    ToState: Optional[str]
    ToCountry: Optional[str]
    NumMedia: int
