import json
import os
import unittest
from unittest.mock import patch, MagicMock

from googleapiclient.discovery import Resource
from google.cloud.secretmanager_v1.types import AccessSecretVersionResponse, SecretPayload

from app.email_sender import EmailSender
from app.exceptions import MissingCredentialsException, GoogleAuthError


class TestEmailSender(unittest.TestCase):
    @patch.dict(os.environ, {}, clear=True)
    @patch("app.email_sender.email_sender.service_account.Credentials")
    @patch("app.email_sender.email_sender.build")
    def test_init_raises_exception_with_missing_envars(self, mock_build, mock_credentials):
        with self.assertRaises(MissingCredentialsException):
            sender = EmailSender()
        mock_build.assert_not_called()
        mock_credentials.from_service_account_info.assert_not_called()

    @patch.dict(
        os.environ,
        {
            "DELEGATED_USER_EMAIL": "test@test.com",
            "PROJECT_ID": "id-1234",
            "SECRET_NAME": "test_secret_name"
        }
    )
    @patch("app.email_sender.email_sender.service_account.Credentials")
    @patch("app.email_sender.email_sender.build")
    def test_init_raises_exception_on_auth_error(self, mock_build, mock_credentials):
        mock_credentials.from_service_account_info.side_effect = ValueError
        with self.assertRaises(GoogleAuthError):
            sender = EmailSender()
        mock_build.assert_not_called()

    @patch.dict(
        os.environ,
        {
            "DELEGATED_USER_EMAIL": "test@test.com",
            "PROJECT_ID": "id-1234",
            "SECRET_NAME": "test_secret_name"
        }
    )
    @patch("app.email_sender.email_sender.service_account.Credentials")
    @patch("app.email_sender.email_sender.build")
    @patch("app.email_sender.email_sender.secretmanager.SecretManagerServiceClient")
    def test_init_creates_service_account(self, mock_secret_manager, mock_build, mock_credentials):

        mock_credentials_file = {
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
        json_str = json.dumps(mock_credentials_file)
        secret_bytes = bytes(json_str, "UTF-8")
        payload = SecretPayload(data=secret_bytes)
        mock_response = AccessSecretVersionResponse(payload=payload)
        mock_secret_client_instance = mock_secret_manager.return_value
        mock_secret_client_instance.access_secret_version.return_value = mock_response

        mock_credentials_instance = MagicMock()
        mock_delegated_credentials_instance = MagicMock()
        mock_service_account = MagicMock(spec=Resource)

        mock_credentials.from_service_account_info.return_value = mock_credentials_instance
        mock_credentials_instance.with_subject.return_value = mock_delegated_credentials_instance
        mock_build.return_value = mock_service_account

        sender = EmailSender()

        mock_credentials.from_service_account_info.assert_called_once_with(
            mock_credentials_file,
            scopes=["https://www.googleapis.com/auth/gmail.send"]
        )
        mock_credentials_instance.with_subject.assert_called_once_with("test@test.com")
        mock_build.assert_called_once_with("gmail", "v1", credentials=mock_delegated_credentials_instance)
        self.assertIs(sender.service, mock_service_account)
