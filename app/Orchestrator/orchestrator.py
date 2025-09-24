import logging

from app.ConfigLoader import ConfigLoader
from app.core.twilio_logic import process_message, sanitize_data

from app.exceptions import OrchestratorMissingMessageData, OrchestratorUnableToProcess, OrchestratorMissingHeaders
from app.models import LogEntry

class Orchestrator:
    """
    Primary control class for handling all steps after a message hits the endpoint
    """
    def __init__(self, config_loader: ConfigLoader, message_data: dict, headers: dict):
        """
        Initializes Orchestrator class and verifies required data exists and is passed to class

        args:
            config_loader (ConfigLoader): object instance of type ConfigLoader or subtype of ConfigLoader
            message_data (dict): raw message data from Twilio webhook request
            headers (dict): request headers in dict format

        Raises:
            OrchestratorMissingMessageData: If message_data is empty or can not be loaded
            OrchestratorMissingHeaders: If headers is empty or can not be loaded
        """
        if not message_data:
            error_log = LogEntry(
                level="ERROR",
                message= "Orchestrator: message_data is empty or missing",
                service_name="Twilio Webhook",
                trace_id=str(headers.get("X-Twilio-Trace-ID", "None")),
                context={},
            )
            logging.error(error_log.to_json())

            raise OrchestratorMissingMessageData("Orchestrator: message_data is empty or missing")
        
        if not headers:
            error_log = LogEntry(
                level="ERROR",
                message= "Orchestrator: headers is empty or missing",
                service_name="Twilio Webhook",
                trace_id="none",
                context=sanitize_data(message_data),
            )
            logging.error(error_log.to_json())

            raise OrchestratorMissingHeaders("Orchestrator: headers is empty or missing")
        
        self.config_loader = config_loader
        self.message_data = message_data
        self.headers = headers
        
        success_log = LogEntry(
            level="INFO",
            message="Orchestrator succesfully created",
            service_name="Twilio Webhook",
            trace_id=str(self.headers.get("X-Twilio-Trace-ID", "None")),
            context=sanitize_data(self.message_data),
        )
        logging.info(success_log.to_json())

    def process_message(self):
        """
        Process messages, extracts required info and returns process message data

        Returns:
            processed_message_data (dict): dict containing required message data for forwarding

        Raises:
            OrchestratorUnableToProcess: If any errors occurs during processing
        """
        try:
            processed_message_data = process_message(self.headers, self.message_data)
            if processed_message_data:
                return processed_message_data
            else:
                raise ValueError("Unknown Error Occured")
        except ValueError as e:
            error_log = LogEntry(
                level="ERROR",
                message=f"Message Processing Error: {str(e)}",
                service_name="Twilio Webhook",
                trace_id=str(self.headers.get("X-Twilio-Trace-ID", "None")),
                context=sanitize_data(self.message_data),
            )
            logging.error(error_log.to_json())

            raise OrchestratorUnableToProcess(f"Unable to Process Messagte: {e}") from e
