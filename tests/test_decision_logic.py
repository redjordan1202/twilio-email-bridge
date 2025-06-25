import unittest
from datetime import datetime

from app.exceptions import RouteProcessingError


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
