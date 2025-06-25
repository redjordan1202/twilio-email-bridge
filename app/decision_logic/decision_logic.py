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
        raise RouteProcessingError(e)


