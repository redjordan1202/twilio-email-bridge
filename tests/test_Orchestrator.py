from datetime import datetime
import unittest
from unittest.mock import MagicMock, patch

from app.Orchestrator import Orchestrator
from app.exceptions import OrchestratorMissingMessageData, OrchestratorUnableToProcess, OrchestratorMissingHeaders

class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        self.dummy_message = {
            "SmsSid": "SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "SmsStatus": "received",
            "MessageSid": "SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "AccountSid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "From": "+11234567890",
            "ApiVersion": '2010-04-01',
            "SmsMessageSid": "SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "NumSegments": "1",
            "To": "+10987654321",
            "ForwardedFrom": "",
            "MessageStatus": "received",
            "Body": "Hello World",
            "FromZip": "",
            "FromCity": "",
            "FromState": "",
            "FromCountry": "",
            "ToZip": "",
            "ToCity": "",
            "ToState": "",
            "ToCountry": "",
            "NumMedia": "0"
        }

        self.dummy_headers = {
            'X-Twilio-Signature': 'fake_signature',
            'x-forwarded-proto': 'https',
            'host': 'example.com',
            'path': 'webhooks/twilio'
        }

        self.mock_config_loader = mock_config_loader = MagicMock()

    def test_orchestrator_raises_error_on_missing_message_data(self):
        with self.assertRaises(TypeError):
            orchestrator = Orchestrator(
                config_loader=self.mock_config_loader,
                headers = self.dummy_headers
                )

    def test_orchestrator_raises_error_on_missing_headers(self):
        with self.assertRaises(TypeError):
            orchestrator = Orchestrator(
                message_data=self.dummy_message,
                config_loader=self.mock_config_loader,
                )

    def test_orchestrator_raises_error_on_missing_config_loader(self):
        with self.assertRaises(TypeError):
            orchestrator = Orchestrator(
                message_data=self.dummy_message,
                headers = self.dummy_headers
                )

    def test_orchestrator_raises_error_on_empty_message_data(self):
        with self.assertRaises(OrchestratorMissingMessageData):
            orchestrator = Orchestrator(
            config_loader=self.mock_config_loader, 
            message_data={},
            headers=self.dummy_headers
            )

    def test_orchestrator_raises_error_on_empty_headers(self):
        with self.assertRaises(OrchestratorMissingHeaders):
            orchestrator = Orchestrator(
            config_loader=self.mock_config_loader, 
            message_data=self.dummy_message,
            headers={}
            )

    @patch('app.core.twilio_logic.process_message')
    def test_orchestrator_calls_process_message_function(self, mock_process_message):
        orchestrator = Orchestrator(
            config_loader=self.mock_config_loader, 
            message_data=self.dummy_message,
            headers=self.dummy_headers
            )
        orchestrator.process_message()
        mock_process_message.assert_called_once_with(self.dummy_message)
