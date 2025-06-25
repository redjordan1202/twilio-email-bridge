import logging
import re

from app.models import LogEntry
from app.exceptions import RouteProcessingError

mfa_code_words = [
    "code",
    "verification",
    "authentication",
    "login",
    "passcode",
    "authentication",
    "access",
    "sign-in"
]


def get_routes(msg: dict) -> dict:
    """
    Filters and sets route field for incoming messages

    Args:
        msg: extracted message data in dict format

    Returns:
        dict: updated message with added routes list.

    Raises:
        RouteProcessingError
    """
    try:
        body = msg["body"]
        routes = []

        if "[CRITICAL]" in body:
            routes = ["email", "text", "discord"]
        elif "[WARNING]" in body:
            routes = ["email", "discord"]
        elif any(word in body for word in mfa_code_words) and re.search(r"\b\d{4,8}\b", body):
            routes = ["email", "text"]
        else:
            routes = ["email"]

        msg["routes"] = routes
        return msg
    except Exception as e:
        failure_log = LogEntry(
            level=logging.ERROR,
            message=e,
            service_name="Message Router",
            trace_id=None,
            context=None
        )
        logging.error(failure_log.to_json())
        raise RouteProcessingError(e)


