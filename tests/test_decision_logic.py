import unittest
from datetime import datetime

from app.exceptions import RouteProcessingError, MissingServeritySectionError, MissingServerityLevelsError
from app.decision_logic import DecisionLogic


class TestDecisionLogic(unittest.TestCase):
    def setUp(self):
        self.dummy_config = {
            "plugins": [
                {
                    "name": "default_email_sender",
                    "type": "smtp_sender",
                    "config": {
                        "recipient_email": "user@domain.com",
                        "smtp_server": "smtp.gmail.com",
                        "smtp_port": 587
                    }
                }
            ],
            "severity_levels": {
                    "normal": ["default_email_sender"],
                    "urgent": ["urgent_email_sender"],
                    "critical": ["critical_email_sender"],
                    "mfa": ["mfa_email_sender"]
            }
        }

        self.dummy_message = {
            'body': "Test Message",
            'from': "5551234567",
            'date_created': datetime.now()
        }

    def test_get_routes_returns_correct_route_for_critical_alerts(self):
        dummy_message = {
            "date_created": datetime.now(),
            "from": "+11234567890",
            "body": "[CRITICAL] - Fake Server Alert",
        }
        expected_result = {
            "date_created": dummy_message["date_created"],
            "from": "+11234567890",
            "body": "[CRITICAL] - Fake Server Alert",
            "routes": ["critical_email_sender"]
        }

        decision_logic = DecisionLogic(message = dummy_message, config = self.dummy_config)
        actual_result = decision_logic.get_routes(dummy_message)
        self.assertEqual(expected_result, actual_result)


    def test_get_routes_returns_correct_route_for_urgent_alerts(self):
        dummy_message = {
            "date_created": datetime.now(),
            "from": "+11234567890",
            "body": "[WARNING] - Fake Server Alert",
        }
        expected_result = {
            "date_created": dummy_message["date_created"],
            "from": "+11234567890",
            "body": "[WARNING] - Fake Server Alert",
            "routes": ["urgent_email_sender"]
        }

        decision_logic = DecisionLogic(message = dummy_message, config = self.dummy_config)
        actual_result = decision_logic.get_routes(dummy_message)
        self.assertEqual(expected_result, actual_result)

    def test_get_routes_returns_correct_route_for_mfa_messages(self):
        dummy_message = {
            "date_created": datetime.now(),
            "from": "+11234567890",
            "body": "code 123456",
        }
        expected_result = {
            "date_created": dummy_message["date_created"],
            "from": "+11234567890",
            "body": "code 123456",
            "routes": ["mfa_email_sender"]
        }

        decision_logic = DecisionLogic(message = dummy_message, config = self.dummy_config)
        actual_result = decision_logic.get_routes(dummy_message)
        self.assertEqual(expected_result, actual_result)

    def test_get_routes_returns_correct_route_for_normal_messages(self):
        dummy_message = {
            "date_created": datetime.now(),
            "from": "+11234567890",
            "body": "Hello World!",
        }
        expected_result = {
            "date_created": dummy_message["date_created"],
            "from": "+11234567890",
            "body": "Hello World!",
            "routes": ["default_email_sender"]
        }

        decision_logic = DecisionLogic(message = dummy_message, config = self.dummy_config)
        actual_result = decision_logic.get_routes(dummy_message)
        self.assertEqual(expected_result, actual_result)

    def test_get_routes_raise_exception_on_processing_error(self):
        dummy_message = {
            "date_created": datetime.now(),
            "from": "+11234567890",
            "body": None,
        }
        with self.assertRaises(RouteProcessingError):
            decision_logic = DecisionLogic(message = dummy_message, config = self.dummy_config)
            decision_logic.get_routes(dummy_message)

    def test_init_function_raises_error_on_missing_message_data(self):
        with self.assertRaises(TypeError):
            decision_logic = DecisionLogic(config = self.dummy_config)

    def test_init_function_raises_error_on_missing_config(self):
        with self.assertRaises(TypeError):
            decision_logic = DecisionLogic(message = self.dummy_message)

    def test_decision_logic_raises_error_on_misisng_severity_section(self):
        dummy_config = {
            "plugins": [
                {
                    "name": "default_email_sender",
                    "type": "smtp_sender",
                    "config": {
                        "recipient_email": "user@domain.com",
                        "smtp_server": "smtp.gmail.com",
                        "smtp_port": 587
                    }
                }
            ]
        }
        with self.assertRaises(MissingServeritySectionError):
            decision_logic = DecisionLogic(message = self.dummy_message, config = dummy_config)

    def test_decision_logic_raises_error_on_missing_severity_level(self):
        dummy_config = {
            "plugins": [
                {
                    "name": "default_email_sender",
                    "type": "smtp_sender",
                    "config": {
                        "recipient_email": "user@domain.com",
                        "smtp_server": "smtp.gmail.com",
                        "smtp_port": 587
                    }
                }
            ],
            "severity_levels": {
                    "normal": ["default_email_sender"],
                    "urgent": ["default_email_sender"],
                    "critical": ["default_email_sender"]
            }
        }

        with self.assertRaises(MissingServerityLevelsError):
            decision_logic = DecisionLogic(message = self.dummy_message, config = dummy_config)
