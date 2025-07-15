import base64
import json
import os
import unittest
from email.parser import Parser
from unittest.mock import patch, MagicMock

from googleapiclient.discovery import Resource
from google.cloud.secretmanager_v1.types import AccessSecretVersionResponse, SecretPayload

from app.email_sender import EmailSender
from app.exceptions import MissingCredentialsException, GoogleAuthError


class TestEmailSender(unittest.TestCase):
    def setUp(self):

        # Setup mock environment variables
        self.mock_env = {
            "DELEGATED_USER_EMAIL": "test@test.com",
            "PROJECT_ID": "id-1234",
            "SECRET_NAME": "test_secret_name"
        }

        self.patcher_environ = patch.dict('os.environ', self.mock_env)
        self.patcher_environ.start()
        self.addCleanup(self.patcher_environ.stop)

        # Setup mock objects needed for EmailSender class initialization
        patcher_credentials = patch("app.email_sender.email_sender.service_account.Credentials")
        patcher_build = patch("app.email_sender.email_sender.build")
        patcher_secret_manager = patch("app.email_sender.email_sender.secretmanager.SecretManagerServiceClient")

        self.mock_credentials = patcher_credentials.start()
        self.mock_build = patcher_build.start()
        self.mock_secret_manager = patcher_secret_manager.start()

        self.mock_credentials_file = {
            "type": "service_account",
            "project_id": "project-id-1234",
            "private_key_id": "private-key-id-1234",
            "private_key": "private-key-value",
            "client_email": "service_account@test.com",
            "client_id": "client-id-1234",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509",
            "universe_domain": "googleapis.com"
        }
        json_str = json.dumps(self.mock_credentials_file)
        secret_bytes = bytes(json_str, "UTF-8")
        payload = SecretPayload(data=secret_bytes)
        mock_response = AccessSecretVersionResponse(payload=payload)

        mock_secret_client_instance = self.mock_secret_manager.return_value
        mock_secret_client_instance.access_secret_version.return_value = mock_response

        self.mock_credentials_instance = MagicMock()
        self.mock_delegated_credentials_instance = MagicMock()
        self.mock_service_account = MagicMock(spec=Resource)

        self.mock_credentials.from_service_account_info.return_value = self.mock_credentials_instance
        self.mock_credentials_instance.with_subject.return_value = self.mock_delegated_credentials_instance
        self.mock_build.return_value = self.mock_service_account

        self.addCleanup(patcher_credentials.stop)
        self.addCleanup(patcher_build.stop)
        self.addCleanup(patcher_secret_manager.stop)

    @patch.dict(os.environ, {}, clear=True)
    def test_init_raises_exception_with_missing_envars(self):
        with self.assertRaises(MissingCredentialsException):
            sender = EmailSender()
        self.mock_build.assert_not_called()
        self.mock_credentials.from_service_account_info.assert_not_called()

    @patch("app.email_sender.email_sender.service_account.Credentials")
    @patch("app.email_sender.email_sender.build")
    def test_init_raises_exception_on_auth_error(self, mock_build, mock_credentials):
        mock_credentials.from_service_account_info.side_effect = ValueError
        with self.assertRaises(GoogleAuthError):
            sender = EmailSender()
        mock_build.assert_not_called()

    def test_init_creates_service_account(self):

        sender = EmailSender()

        self.mock_credentials.from_service_account_info.assert_called_once_with(
            self.mock_credentials_file,
            scopes=["https://www.googleapis.com/auth/gmail.send"]
        )
        self.mock_credentials_instance.with_subject.assert_called_once_with("test@test.com")
        self.mock_build.assert_called_once_with("gmail", "v1", credentials=self.mock_delegated_credentials_instance)
        self.assertIs(sender.service, self.mock_service_account)

    def test_build_email_requires_destination(self):
        with self.assertRaises(ValueError) as e:
            email = EmailSender.build_email("", "Body", "Subject")
        self.assertEqual(str(e.exception), "Destination must not be empty")

    def test_build_email_requires_body(self):
        with self.assertRaises(ValueError) as e:
            email = EmailSender.build_email("to@email.com", "", "Subject")
        self.assertEqual(str(e.exception), "Body must not be empty")

    def test_build_email_requires_subject(self):
        with self.assertRaises(ValueError) as e:
            email = EmailSender.build_email("to@email.com", "Body", "")
        self.assertEqual(str(e.exception), "Subject must not be empty")

    def test_build_email_raises_exception_on_invalid_address(self):
        with self.assertRaises(ValueError) as e:
            email = EmailSender.build_email("toemail.com", "Body", "Subject")
        self.assertEqual(str(e.exception), "Invalid address")

    def test_build_email_returns_encoded_email(self):
        to = "to@email.com"
        body = "Body"
        subject = "Subject"

        result = EmailSender.build_email(to, body, subject)
        decoded_bytes = base64.urlsafe_b64decode(result)
        decoded_email = decoded_bytes.decode("UTF-8")

        parser = Parser()
        parsed_result = parser.parsestr(decoded_email)

        self.assertEqual(to, parsed_result["to"])
        self.assertEqual(body, parsed_result.get_payload())
        self.assertEqual(subject, parsed_result["subject"])
