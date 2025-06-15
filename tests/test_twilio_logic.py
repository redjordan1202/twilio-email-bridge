import os
import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

from twilio.base.exceptions import TwilioRestException
from twilio.rest.api.v2010.account.message import MessageInstance

from app.core.twilio_logic import get_full_twilio_data, extract_message_info, get_client
from app.exceptions import ClientAuthenticationException, RequiresClientException, ResourceNotFoundException, \
    MissingCredentialsException


class TwilioLogicTest(unittest.TestCase):

    def test_extract_message_info_raises_error_on_missing_field(self):
        twilio_data = MagicMock(spec=MessageInstance)
        with self.assertRaises(AttributeError):
            extract_message_info(twilio_data)

    def test_extract_message_info_raises_error_on_blank_field(self):
        msg_data = MagicMock(spec=MessageInstance)
        msg_data.body = "Test Body"
        msg_data.from_ = "+11234567890"
        msg_data.date_created = None
        with self.assertRaises(ValueError):
            extract_message_info(msg_data)

    def test_extract_message_info_returns_dict(self):
        msg_data = MagicMock(spec=MessageInstance)
        msg_data.body = "Test Body"
        msg_data.from_ = "+11234567890"
        msg_data.date_created = datetime.now()

        data = extract_message_info(msg_data)
        self.assertIsInstance(data, dict)
        self.assertEqual(data['body'], msg_data.body)
        self.assertEqual(data['from'], msg_data.from_)
        self.assertEqual(data['date_created'], msg_data.date_created)



    def test_get_full_twilio_data_raises_error_on_missing_client(self):
        with self.assertRaises(RequiresClientException):
            get_full_twilio_data(client=None, msg_sid="Fake Sid")

    def test_get_full_twilio_data_raises_error_on_missing_message_sid(self):
        fake_client = MagicMock()
        with self.assertRaises(ValueError):
            get_full_twilio_data(client=fake_client, msg_sid=None)

    def test_get_full_twilio_data_raises_error_on_invalid_message_sid(self):
        fake_client = MagicMock()
        fake_client.messages.return_value.fetch.side_effect = TwilioRestException(
            status=404,
            uri="/2010-04-01/Accounts/AC.../Messages/SM_not_found",
            msg="The requested resource was not found"
        )
        with self.assertRaises(ResourceNotFoundException):
            get_full_twilio_data(client=fake_client, msg_sid="invalid_sid")


    def test_get_full_twilio_data_returns_message(self):
        mock_return_message = MagicMock(spec=MessageInstance)
        fake_client = MagicMock()
        fake_client.messages.return_value.fetch.return_value = mock_return_message

        msg = get_full_twilio_data(client=fake_client, msg_sid="valid_sid")

        self.assertIs(msg, mock_return_message)
        self.assertIsInstance(msg, MessageInstance)


    def test_get_client_raises_error_on_missing_credentials(self):
        with self.assertRaises(MissingCredentialsException):
            get_client()

    @patch('app.core.twilio_logic.Client')
    @patch.dict(os.environ, {'TWILIO_ACCOUNT_SID': 'AC123', 'TWILIO_AUTH_TOKEN': 'AC456'})
    def test_get_client_returns_client(self, mock_twilio_client):
        get_client()
        mock_twilio_client.assert_called_once()
        mock_twilio_client.assert_called_once_with(
            'AC123',
            'AC456'
        )

    @patch('app.core.twilio_logic.Client')
    @patch.dict(os.environ, {'TWILIO_ACCOUNT_SID': 'AC123', 'TWILIO_AUTH_TOKEN': 'AC456'})
    def test_get_client_raises_exception_on_incorrect_credentials(self, mock_twilio_client):
        mock_twilio_client.side_effect = TwilioRestException(
            status=401,
            uri="/2010-04-01/Accounts/AC_fake_sid",
            msg="Authentication Error"
        )

        with self.assertRaises(ClientAuthenticationException):
            get_client()