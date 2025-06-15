import os
import unittest
from unittest.mock import patch


class TwilioLogicTest(unittest.TestCase):

    def test_extract_message_info_raises_error_on_missing_field(self):
        from app.core.twilio_logic import extract_message_info
        twilio_data = {}
        with self.assertRaises(AttributeError):
            extract_message_info(twilio_data)


    def test_get_full_twilio_data_raises_error_on_missing_client(self):
        from app.core.twilio_logic import get_full_twilio_data
        from app.exceptions import RequiresClientException
        with self.assertRaises(RequiresClientException):
            get_full_twilio_data("")


    def test_get_client_raises_error_on_missing_credentials(self):
        from app.core.twilio_logic import get_client
        from app.exceptions import MissingCredentialsException
        with self.assertRaises(MissingCredentialsException):
            get_client()

    @patch('twilio.rest.Client')
    @patch.dict(os.environ, {'TWILIO_ACCOUNT_SID': 'AC123', 'TWILIO_AUTH_TOKEN': 'AC456'})
    def test_get_client_returns_client(self, mock_twilio_client):
        from app.core.twilio_logic import get_client
        get_client()
        mock_twilio_client.assert_called_once()
        mock_twilio_client.assert_called_once_with(
            'AC123',
            'AC456'
        )