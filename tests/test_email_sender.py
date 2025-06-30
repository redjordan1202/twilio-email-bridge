import os
import unittest
from unittest.mock import patch, MagicMock

from googleapiclient.discovery import Resource

from app.email_sender import EmailSender
from app.exceptions import MissingCredentialsException, GoogleAuthError


class TestEmailSender(unittest.TestCase):
    @patch("app.email_sender.email_sender.service_account.Credentials")
    @patch("app.email_sender.email_sender.build")
    @patch.dict(os.environ, {}, clear=True)
    def test_init_raises_exception_with_missing_envars(self, mock_build, mock_credentials):
        with self.assertRaises(MissingCredentialsException):
            sender=EmailSender()
        mock_build.assert_not_called()
        mock_credentials.from_service_account_file.assert_not_called()

    @patch.dict(
        os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "file.json", "DELEGATED_USER_EMAIL": "test@test.com"}
    )
    @patch("app.email_sender.email_sender.service_account.Credentials")
    @patch("app.email_sender.email_sender.build")
    def test_init_raises_exception_on_auth_error(self, mock_build, mock_credentials):
        mock_credentials.from_service_account_file.side_effect = ValueError
        with self.assertRaises(GoogleAuthError):
            sender=EmailSender()
        mock_build.assert_not_called()

    @patch.dict(
        os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "file.json", "DELEGATED_USER_EMAIL": "test@test.com"}
    )
    @patch("app.email_sender.email_sender.service_account.Credentials")
    @patch("app.email_sender.email_sender.build")
    def test_init_creates_service_account(self, mock_build, mock_credentials):
        mock_credentials_instance = MagicMock()
        mock_delegated_credentials_instance = MagicMock()
        mock_service_account = MagicMock(spec=Resource)

        mock_credentials.from_service_account_file.return_value = mock_credentials_instance
        mock_credentials_instance.with_subject.return_value = mock_delegated_credentials_instance
        mock_build.return_value = mock_service_account

        sender = EmailSender()

        mock_credentials.from_service_account_file.assert_called_once_with(
            "file.json",
            scopes=["https://www.googleapis.com/auth/gmail.send"]
        )
        mock_credentials_instance.with_subject.assert_called_once_with("test@test.com")
        mock_build.assert_called_once_with("gmail", "v1", credentials=mock_delegated_credentials_instance)
        self.assertIs(sender.service, mock_service_account)
