import json
import os
import logging
import base64
import re
from email.mime.text import MIMEText

from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.auth.exceptions import GoogleAuthError
from google.cloud import secretmanager

from app.exceptions import MissingCredentialsException, GoogleAuthError as CustomGoogleAuthError
from app.models import LogEntry


class EmailSender:
    """
    Handles authentication and sending of emails via Google APIs

    This class uses a Google Cloud Service Account with Domain-Wide Delegation to send emails as a group inbox.
    Uses Google Secret Manager to access service account details for authentication

    Attributes:
        service (googleapiclient.discovery.Resource): Google Cloud Service Account service object.

    """
    def __init__(self):
        """
        Initializes the EmailSender object by authenticating with Google APIs using a service account.

        Raises:
            MissingCredentialsException: If required environment variables are not set.
            CustomGoogleAuthError: If authentication with Google APIs fails.
        """
        delegated_user_email = os.environ.get("DELEGATED_USER_EMAIL", None)
        project_id = os.environ.get("PROJECT_ID", None)
        secret_name = os.environ.get("SECRET_NAME", None)
        scopes = ["https://www.googleapis.com/auth/gmail.send"]

        if not all([delegated_user_email, project_id, secret_name]):
            failure_log = LogEntry(
                level="ERROR",
                message="Missing required environment variables.",
                service_name="EmailSender",
                trace_id=None, # Trace ID and context will be filled out by the background task orchestrator
                context=None
            )
            logging.error(failure_log.to_json())
            raise MissingCredentialsException("Required credentials are missing.")

        try:
            secret_client = secretmanager.SecretManagerServiceClient()
            secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
            response = secret_client.access_secret_version(request={"name": secret_path})
            payload = response.payload.data.decode("UTF-8")
            credentials_info = json.loads(payload)

            credentials = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=scopes
            )
            delegated_credentials = credentials.with_subject(delegated_user_email)

            self.service = build('gmail', 'v1', credentials=delegated_credentials)
        except (ValueError, FileNotFoundError, TypeError, GoogleAuthError) as e:
            failure_log = LogEntry(
                level="ERROR",
                message=f"Error during authentication with Google APIs. {str(e)}",
                service_name="EmailSender",
                trace_id=None,  # Trace ID and context will be filled out by the background task orchestrator error log
                context=None
            )
            logging.error(failure_log.to_json())
            raise CustomGoogleAuthError("Failed to authenticate with Google APIs.") from e
    @staticmethod
    def build_email(destination: str, body: str, subject: str) -> str:
        if not destination:
            raise ValueError("Destination must not be empty")
        if not subject:
            raise ValueError("Subject must not be empty")
        if not body:
            raise ValueError("Body must not be empty")

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', destination):
            raise ValueError("Invalid address")
        message = MIMEText(body)
        message["to"] = destination
        message["subject"] = subject
        message["from"] = "me"

        return base64.urlsafe_b64encode(message.as_bytes()).decode("UTF-8")
