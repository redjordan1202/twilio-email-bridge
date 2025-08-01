import os
import logging
from datetime import datetime

from twilio.base.exceptions import TwilioRestException
from twilio.request_validator import RequestValidator
from twilio.rest.api.v2010.account.message import MessageInstance
from fastapi import Request, Form

from app.exceptions.exceptions import MissingCredentialsException, ClientAuthenticationException, \
    RequiresClientException, ResourceNotFoundException, InvalidTwilioRequestException, RouteProcessingError
from twilio.rest import Client

from app.models import LogEntry

from app.decision_logic import get_routes

from app.email_sender import EmailSender


def get_client() -> Client:
    """
    Gets a twilio client instance

    Returns:
        twilio.rest.Client: Twilio client instance

    Raises:
        MissingCredentialsException: If no credentials are provided
        ClientAuthenticationException: If unable to authenticate with Twilio
    """
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    if not account_sid or not auth_token:
        raise MissingCredentialsException("Required credentials are missing")

    try:
        client = Client(account_sid, auth_token)
        return client
    except TwilioRestException as e:
        raise ClientAuthenticationException("Twilio Authentication Failed") from e

def validate_twilio_request(request: Request, data: dict) -> bool:
    """
    Validates a Twilio request

    Args:
        request: Request to fastAPI endpoint
        data: Raw twilio request data. (Must not be modified for validator to work)

    Returns:
        bool: True if valid, False otherwise
    """
    validator = RequestValidator(os.environ["TWILIO_AUTH_TOKEN"])
    is_valid = validator.validate(
        str(request.url),
        data,
        request.headers.get("X-Twilio-Signature", "")
    )
    return is_valid

def get_full_twilio_data(client: Client, msg_sid: str) -> MessageInstance:
    """
    Pulls full message data from twilio
    Args:
        client: Twilio client instance
        msg_sid: MessageSid of message being fetched

    Returns:
        MessageInstance: Instance of the twilio message with all data

    Raises:
        ValueError: If msg_sid is empty
        ResourceNotFoundException: If no message is found
    """
    if not client:
        raise RequiresClientException("Client is required")
    if not msg_sid:
        raise ValueError("msg_sid is required")

    try:
        message = client.messages(msg_sid).fetch()
        return message
    except TwilioRestException as e:
        if e.status == 404:
            raise ResourceNotFoundException(f"Resource not found: {msg_sid}")
        else:
            raise e


def extract_message_info(twilio_data: MessageInstance) -> dict:
    """
    Extracts required message data from twilio MessageInstance
    Args:
        twilio_data: Instance of twilio MessageInstance to extract data from

    Returns:
        dict: Dictionary of extracted data for future processing

    Raises:
        AttributeError: if any required fields are missing
        ValueError: if any required fields are present but empty
    """
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
    """
    Sanitizes data for logging purposes

    Args:
        data: The message data to be sanitized. Typically, the raw message data.

    Returns:
        dict: Dictionary of sanitized data
    """
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


def twilio_background_task(request: Request, data: dict) -> dict | None:
    """
    Function to be called as a background task
    Runs all functions needed to process twilio messages

    Args:
        request: Request to fastAPI endpoint
        data: Raw twilio request data. (Must not be modified for validator to work)

    Returns:
        dict: dictionary of extracted data for future processing
        None: returned on error.
    """
    try:
        client = get_client()
        msg_sid = data.get("MessageSid")
        if not msg_sid:
            raise ValueError("MessageSid is required in the data")
        full_twilio_data = get_full_twilio_data(client, msg_sid)
        extracted_info = extract_message_info(full_twilio_data)
        extracted_info = get_routes(extracted_info)
        if "email" in extracted_info["routes"]:
            sender = EmailSender()
            encoded_msg = sender.build_email(
                destination=os.environ["MY_EMAIL"],
                subject=f"New Text Message from {extracted_info['from']}",
                body=extracted_info["body"],
            )
            sender.send_email(encoded_msg)

        success_log = LogEntry(
            level="INFO",
            message="SMS Processed Successfully",
            service_name="Twilio Webhook",
            trace_id=request.headers.get("X-Twilio-Trace-ID", "None"),
            context=sanitize_data(data),
        )
        logging.info(success_log.to_json())

    except (
            MissingCredentialsException,
            ClientAuthenticationException,
            RequiresClientException,
            ResourceNotFoundException,
            RouteProcessingError
    ) as e:
        try:
            sanitized_data = sanitize_data(data)
        except ValueError:
            sanitized_data = {"MessageSid": "MessageSid Not Found"}
        failure_log = LogEntry(
            level="ERROR",
            message= str(e),
            service_name="Twilio Webhook",
            trace_id=request.headers.get("X-Twilio-Trace-ID", "None"),
            context=sanitized_data,
        )
        logging.error(failure_log.to_json())
        return None
