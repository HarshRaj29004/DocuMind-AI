from __future__ import annotations

import os
import io
from typing import Optional
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/drive"]

class GoogleDriveStore:
    """Manager for uploading files to Google Drive."""

    def __init__(self) -> None:
        """
        Initialize Google Drive client.
        Supports OAuth client credentials (GOOGLE_OAUTH_CLIENT_JSON)
        and service account credentials (GOOGLE_SERVICE_ACCOUNT_JSON).
        """
        self._service = None
        self._default_folder_id = (os.getenv("GOOGLE_DRIVE_FOLDER_ID") or "").strip()
        self._setup_credentials()

    def _setup_credentials(self) -> None:
        """Set up Google Drive API authentication."""
        oauth_client_path = os.getenv("GOOGLE_OAUTH_CLIENT_JSON").strip()
        service_account_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON").strip()

        if oauth_client_path and os.path.exists(oauth_client_path):
            flow = InstalledAppFlow.from_client_secrets_file(oauth_client_path, SCOPES)
            creds = flow.run_local_server(port=0)
            self._service = build("drive", "v3", credentials=creds)
            return

        if service_account_path and os.path.exists(service_account_path):
            creds = Credentials.from_service_account_file(
                service_account_path, scopes=SCOPES
            )
            self._service = build("drive", "v3", credentials=creds)
            return

        raise RuntimeError(
            "Google Drive credentials not configured. "
            "Set GOOGLE_OAUTH_CLIENT_JSON or GOOGLE_SERVICE_ACCOUNT_JSON env var."
        )

    def upload_file(
        self,
        file_content: bytes,
        filename: str,
        folder_id: Optional[str] = None,
        mimetype: str = "text/plain",
    ) -> str:
        """
        Upload a file to Google Drive.

        Args:
            file_content: Raw bytes of the file
            filename: Name of the file (used as Google Drive file name)
            folder_id: Optional Google Drive folder ID to upload to
            mimetype: MIME type of the file

        Returns:
            Google Drive file ID of the uploaded file
        """
        if not self._service:
            raise RuntimeError("Google Drive service not initialized")

        file_metadata = {"name": filename}
        target_folder_id = folder_id or self._default_folder_id
        if target_folder_id:
            file_metadata["parents"] = [target_folder_id]
        else:
            raise RuntimeError(
                "No Google Drive target folder configured. "
                "Set GOOGLE_DRIVE_FOLDER_ID to a folder in a Shared Drive and share it with the service account."
            )

        # Create media stream from bytes
        media = MediaIoBaseUpload(
            io.BytesIO(file_content), mimetype=mimetype, resumable=True
        )

        file_obj = (
            self._service.files()
            .create(
                body=file_metadata,
                media_body=media,
                fields="id",
                supportsAllDrives=True,
            )
            .execute()
        )

        return file_obj.get("id")

    def get_or_create_folder(self, folder_name: str) -> str:
        """
        Get or create a folder in Google Drive root.

        Args:
            folder_name: Name of the folder

        Returns:
            Google Drive folder ID
        """
        if not self._service:
            raise RuntimeError("Google Drive service not initialized")

        # Search for existing folder
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = (
            self._service.files()
            .list(
                q=query,
                spaces="drive",
                fields="files(id)",
                pageSize=1,
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
            )
            .execute()
        )
        files = results.get("files", [])

        if files:
            return files[0]["id"]

        # Create new folder
        file_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        folder = (
            self._service.files()
            .create(body=file_metadata, fields="id", supportsAllDrives=True)
            .execute()
        )
        return folder.get("id")
