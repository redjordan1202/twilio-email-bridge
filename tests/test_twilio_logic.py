import os
import unittest
from datetime import datetime
from logging import Logger
from unittest.mock import patch, MagicMock

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
from twilio.rest.api.v2010.account.message import MessageInstance

from app.core.twilio_logic import get_full_twilio_data, extract_message_info, get_client, validate_twilio_request, \
    twilio_background_task, sanitize_data
from app.exceptions import ClientAuthenticationException, RequiresClientException, ResourceNotFoundException, \
    MissingCredentialsException, InvalidTwilioRequestException


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
        with patch.dict(os.environ, {}, clear=True):
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

    @patch('app.core.twilio_logic.RequestValidator')
    @patch.dict(os.environ, {'TWILIO_AUTH_TOKEN': 'fake_token'})
    def test_validate_twilio_request_returns_true(self, mock_validator):
        mock_validator.return_value.validate.return_value = True
        mock_request = MagicMock()
        mock_request.url.path = '/webhooks/twilio'
        mock_request.headers = {'X-Twilio-Signature': 'fake_signature'}
        data = {'key': 'value'}
        is_valid = validate_twilio_request(mock_request, data)
        self.assertTrue(is_valid)

    @patch('app.core.twilio_logic.RequestValidator')
    @patch.dict(os.environ, {'TWILIO_AUTH_TOKEN': 'fake_token'})
    def test_validate_twilio_request_returns_false(self, mock_validator):
        mock_validator.return_value.validate.return_value = False
        mock_request = MagicMock()
        mock_request.url.path = '/webhooks/twilio'
        mock_request.headers = {'X-Twilio-Signature': 'fake_signature'}
        data = {'key': 'value'}
        is_valid = validate_twilio_request(mock_request, data)
        self.assertFalse(is_valid)

    @patch.dict(os.environ, {'MY_EMAIL': 'email@example.com'})
    @patch('app.core.twilio_logic.get_routes')
    @patch('app.core.twilio_logic.EmailSender')
    @patch('app.core.twilio_logic.get_client')
    @patch('app.core.twilio_logic.get_full_twilio_data')
    @patch('app.core.twilio_logic.extract_message_info')
    def test_background_task_function_calls_all_functions_correctly(
            self,
            mock_extract_message_info,
            mock_get_full_twilio_data,
            mock_get_client,
            mock_email_sender,
            mock_get_routes,
        ):
        mock_request = MagicMock()
        mock_request.url.path = '/webhooks/twilio'
        mock_request.headers = {'X-Twilio-Signature': 'fake_signature'}
        mock_data = {'MessageSid': 'fake_msg_sid', 'key': 'value'}
        mock_client = MagicMock(spec=Client)
        mock_message_instance = MagicMock(spec=MessageInstance)
        mock_message_instance.body = "Test Body"
        mock_message_instance.from_ = "+11234567890"
        mock_message_instance.date_created = datetime.now()
        mock_sender_instance = mock_email_sender.return_value

        mock_get_client.return_value = mock_client
        mock_get_full_twilio_data.return_value = mock_message_instance
        mock_extract_message_info.return_value = {
            'body': mock_message_instance.body,
            'from': mock_message_instance.from_,
            'date_created': mock_message_instance.date_created
        }
        mock_get_routes.return_value = {
            'body': mock_message_instance.body,
            'from': mock_message_instance.from_,
            'date_created': mock_message_instance.date_created,
            'routes': "email"
        }

        twilio_background_task(mock_request, mock_data)

        mock_get_client.assert_called_once()
        mock_get_full_twilio_data.assert_called_once_with(mock_client, mock_data['MessageSid'])
        mock_extract_message_info.assert_called_once_with(mock_message_instance)
        mock_email_sender.assert_called_once()
        mock_sender_instance.build_email.assert_called_once()
        mock_sender_instance.send_email.assert_called_once()

    @patch('app.core.twilio_logic.validate_twilio_request')
    @patch('app.core.twilio_logic.logging.error')
    def test_background_task_function_logs_error_on_invalid_request (self,mock_logger, mock_validate_twilio_request):
        mock_validate_twilio_request.return_value = False
        mock_request = MagicMock()
        mock_request.url.path = '/webhooks/twilio'
        mock_request.headers = {'X-Twilio-Signature': 'fake_signature'}
        mock_data = {'MessageSid': 'fake_msg_sid', 'key': 'value'}

        twilio_background_task(mock_request, mock_data)
        mock_logger.assert_called_once()


    @patch('app.core.twilio_logic.validate_twilio_request')
    @patch('app.core.twilio_logic.get_client')
    @patch('app.core.twilio_logic.logging.error')
    def test_background_task_function_logs_error_when_exception_is_raised(
            self,
            mock_logger,
            mock_get_client,
            mock_validate_twilio_request
    ):
        mock_request = MagicMock()
        mock_request.url.path = '/webhooks/twilio'
        mock_request.headers = {'X-Twilio-Signature': 'fake_signature'}
        mock_data = {'MessageSid': 'fake_msg_sid', 'key': 'value'}
        mock_client = MagicMock(spec=Client)
        mock_message_instance = MagicMock(spec=MessageInstance)
        mock_message_instance.body = "Test Body"
        mock_message_instance.from_ = "+11234567890"
        mock_message_instance.date_created = datetime.now()

        mock_validate_twilio_request.return_value = True
        mock_get_client.side_effect = ClientAuthenticationException("Required credentials are missing")

        twilio_background_task(mock_request, mock_data)
        mock_logger.assert_called_once()



    def test_sanitize_data_returns_valid_dict(self):
        dummy_message = {
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

        expected_dict = {
            "MessageSid": "SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "AccountSid": dummy_message['AccountSid'][-4:],
            "ApiVersion": '2010-04-01',
            "MessageStatus": "received",
            "NumMedia": "0"
        }

        result = sanitize_data(dummy_message)
        self.assertIsInstance(result, dict)
        self.assertEqual(result, expected_dict)


    def test_sanitize_data_returns_valid_dict_when_missing_fields(self):
        expected_dict = {
            "MessageSid": "SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "AccountSid":"",
            "ApiVersion": "",
            "MessageStatus": "",
            "NumMedia": ""
        }

        result = sanitize_data({"MessageSid": "SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"})
        self.assertIsInstance(result, dict)
        self.assertEqual(result, expected_dict)

    def test_sanitize_data_raises_exception_if_missing_messagesid(self):
        with self.assertRaises(ValueError):
            sanitize_data({})
