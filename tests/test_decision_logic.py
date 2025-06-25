import unittest
from datetime import datetime

from app.exceptions import RouteProcessingError
from app.decision_logic import get_routes


class TestDecisionLogic(unittest.TestCase):

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
            "routes": ["email", "text", "discord"]
        }

        actual_result = get_routes(dummy_message)
        self.assertEqual(expected_result, actual_result)


    def test_get_routes_returns_correct_route_for_warning_alerts(self):
        dummy_message = {
            "date_created": datetime.now(),
            "from": "+11234567890",
            "body": "[WARNING] - Fake Server Alert",
        }
        expected_result = {
            "date_created": dummy_message["date_created"],
            "from": "+11234567890",
            "body": "[WARNING] - Fake Server Alert",
            "routes": ["email", "discord"]
        }

        actual_result = get_routes(dummy_message)
        self.assertEqual(expected_result, actual_result)

    def test_get_routes_returns_correct_route_for_2fa_messages(self):
        dummy_message = {
            "date_created": datetime.now(),
            "from": "+11234567890",
            "body": "code 123456",
        }
        expected_result = {
            "date_created": dummy_message["date_created"],
            "from": "+11234567890",
            "body": "code 123456",
            "routes": ["email", "text"]
        }

        actual_result = get_routes(dummy_message)
        self.assertEqual(expected_result, actual_result)

    def test_get_routes_returns_correct_route_for_regular_messages(self):
        dummy_message = {
            "date_created": datetime.now(),
            "from": "+11234567890",
            "body": "Hello World!",
        }
        expected_result = {
            "date_created": dummy_message["date_created"],
            "from": "+11234567890",
            "body": "Hello World!",
            "routes": ["email"]
        }

        actual_result = get_routes(dummy_message)
        self.assertEqual(expected_result, actual_result)

    def test_get_routes_raise_exception_on_processing_error(self):
        dummy_message = {
            "date_created": datetime.now(),
            "from": "+11234567890",
            "body": None,
        }
        with self.assertRaises(RouteProcessingError):
            get_routes(dummy_message)
