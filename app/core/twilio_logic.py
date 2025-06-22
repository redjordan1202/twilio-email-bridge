import os
import logging
from datetime import datetime

from twilio.base.exceptions import TwilioRestException
from twilio.request_validator import RequestValidator
from twilio.rest.api.v2010.account.message import MessageInstance
from fastapi import Request, Form

from app.exceptions.exceptions import MissingCredentialsException, ClientAuthenticationException, \
    RequiresClientException, ResourceNotFoundException, InvalidTwilioRequestException
from twilio.rest import Client

from app.models import LogEntry


def get_client() -> Client:
    account_sid = os.environ["TWILIO_ACCOUNT_SID"] if "TWILIO_ACCOUNT_SID" in os.environ else None
    auth_token = os.environ["TWILIO_AUTH_TOKEN"] if "TWILIO_AUTH_TOKEN" in os.environ else None
    if not account_sid or not auth_token:
        raise MissingCredentialsException("Required credentials are missing")

    try:
        client = Client(account_sid, auth_token)
        return client
    except TwilioRestException as e:
        raise ClientAuthenticationException("Twilio Authentication Failed") from e

def validate_twilio_request(request: Request, data: dict) -> bool:
        validator = RequestValidator(os.environ["TWILIO_AUTH_TOKEN"])
        is_valid = validator.validate(
            str(request.url),
            data,
            request.headers.get("X-Twilio-Signature", "")
        )
        if is_valid:
            return True
        else:
            return False

def get_full_twilio_data(client: Client, msg_sid: str) -> MessageInstance:
    if not client:
        raise RequiresClientException("Client is required")
    if not msg_sid:
        raise ValueError("msg_sid is required")

    try:
        message = client.messages(msg_sid).fetch()
        print(type(message))
        print(message)
        return message
    except TwilioRestException as e:
        if e.status == 404:
            raise ResourceNotFoundException(f"Resource not found: {msg_sid}")
        else:
            raise e


def extract_message_info(twilio_data: MessageInstance) -> dict:
    required_fields = ["from_", "body", "date_created"]
    for field in required_fields:
        if not hasattr(twilio_data, field):
            raise AttributeError(f"Required field {field} is missing")
        if not getattr(twilio_data, field):
            raise ValueError(f"Required field {field} is present but empty")

    return {
        "date_created": twilio_data.date_created,
        "from": twilio_data.from_,
        "body": twilio_data.body,
    }


def sanitize_data(data: dict) -> dict:
    message_sid = data.get("MessageSid",None)
    if not message_sid:
        raise ValueError("MessageSid is required")

    account_sid = data.get("AccountSid", "")

    return {
        "MessageSid": message_sid,
        "AccountSid": account_sid[-4:] if account_sid else "",
        "ApiVersion": data.get("ApiVersion", ""),
        "MessageStatus": data.get("MessageStatus", ""),
        "NumMedia": data.get("NumMedia", ""),
    }


def twilio_background_task(request: Request, data: dict) -> dict:
    if not validate_twilio_request(request, data):
        failure_log = LogEntry(
            timestamp=datetime.now(),
            level="ERROR",
            message="Twilio request is invalid",
            service_name="Twilio Webhook",
            trace_id=request.headers.get("X-Twilio-Trace-ID", "None"),
            context={
                "message_sid": data.get("MessageSid", "")
            }
        )
        logging.error(failure_log.to_json())
        raise InvalidTwilioRequestException("Invalid Twilio request")

    try:
        client = get_client()
        msg_sid = data.get("MessageSid")
        if not msg_sid:
            raise ValueError("MessageSid is required in the data")
        full_twilio_data = get_full_twilio_data(client, msg_sid)
        extracted_info = extract_message_info(full_twilio_data)
        success_log = LogEntry(
            timestamp=datetime.now(),
            level="INFO",
            message="SMS Processed Successfully",
            service_name="Twilio Webhook",
            trace_id=request.headers.get("X-Twilio-Trace-ID", "None"),
            context=sanitize_data(data),
        )
        logging.info(success_log.to_json())
        return extracted_info
    except (
            MissingCredentialsException,
            ClientAuthenticationException,
            RequiresClientException,
            ResourceNotFoundException
    ) as e:
        try:
            sanitized_data = sanitize_data(data)
        except ValueError:
            sanitized_data = {"MessageSid": "MessageSid Not Found"}
        failure_log = LogEntry(
            timestamp=datetime.now(),
            level="ERROR",
            message= str(e),
            service_name="Twilio Webhook",
            trace_id=request.headers.get("X-Twilio-Trace-ID", "None"),
            context=sanitized_data,
        )
        logging.error(failure_log.to_json())
        raise e