import logging
import re

from app.models import LogEntry
from app.exceptions import RouteProcessingError, MissingServeritySectionError, MissingServerityLevelsError, \
    DecisionLogicMessageMissing, DecisionLogicConfigMissing


class DecisionLogic:
    """
    This class handles routing of messages that come in. 
    Uses config file to determine what senders to assign to each level of 
    severity for messages
    """

    def __init__(self, message: dict, config: dict):
        """
        Initializes DecisionLogic object. 
        Recieves and verifies message data and config during initialization

        Args:
            message (dict): Extracted message data from process_messages function
            config (dict): Extracted config data from ConfigLoader class

        Raises:
            DecisionLogicMessageMissing: If message arg is empty or missing
            DecisionLogicConfigMissing: If config arg is empty or missing
            MissingServeritySectionError: If config is missing severity section
            MissingServerityLevelsError: If config is missing one or more severity types
        """

        if not message:
            error_log = LogEntry(
                level="ERROR",
                message= "DecisionLogic: message is empty or missing",
                service_name="Twilio Webhook",
                trace_id="none",
                context={},
            )
            logging.error(error_log.to_json())
            raise DecisionLogicMessageMissing("Message is missing or blank")
        
        if not config:
            error_log = LogEntry(
                level="ERROR",
                message= "DecisionLogic: config is empty or missing",
                service_name="Twilio Webhook",
                trace_id="none",
                context={},
            )
            logging.error(error_log.to_json())
            raise DecisionLogicConfigMissing("Config is missing or blank")
        
        self.severity_levels = [
            "normal", "urgent", "critical", "mfa"
        ]
        self.mfa_code_words = [
            "code",
            "verification",
            "authentication",
            "login",
            "passcode",
            "authentication",
            "access",
            "sign-in"
        ]

        self.message = message
        self.config = config

        if "severity_levels" not in config.keys():
            error_log = LogEntry(
                level="ERROR",
                message= "DecisionLogic: config is missing severity levels section",
                service_name="Twilio Webhook",
                trace_id="none",
                context={},
            )
            logging.error(error_log.to_json())
            raise MissingServeritySectionError("config is missing severity levels section")
        
        missing_levels = self.severity_levels - self.config["severity_levels"].keys()
        if missing_levels:
            error_log = LogEntry(
                level="ERROR",
                message= "DecisionLogic: config is missing one or more severity levels",
                service_name="Twilio Webhook",
                trace_id="none",
                context={},
            )
            logging.error(error_log.to_json())
            raise MissingServerityLevelsError("Config is missing one or more severity levels")

    def get_routes(self) -> dict:
        """
        Filters and sets route field for incoming messages

        Returns:
            dict: updated message with added routes list.

        Raises:
            RouteProcessingError
        """
        try:
            body = self.message["body"]
            routes = []

            if not body:
                raise RouteProcessingError("Body of message can not be empty")

            if "[CRITICAL]" in body:
                routes = self.config["severity_levels"]["critical"]
            elif "[WARNING]" in body:
                routes = self.config["severity_levels"]["urgent"]
            elif any(word in body for word in self.mfa_code_words) and re.search(r"\b\d{4,8}\b", body):
                routes = self.config["severity_levels"]["mfa"]
            else:
                routes = self.config["severity_levels"]["normal"]

            self.message["routes"] = routes
            return self.message
        
        except Exception as e:
            failure_log = LogEntry(
                level="ERROR",
                message=str(e),
                service_name="Message Router",
                trace_id=None,
                context=None
            )
            logging.error(failure_log.to_json())
            raise RouteProcessingError(str(e))
