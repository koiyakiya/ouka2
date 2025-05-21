import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from io import BytesIO
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from typing import Union
from async_lru import alru_cache
from dataclasses import dataclass

ID = Union[str, None]

@dataclass(slots=True)
class ImageData:
    content: bytes
    file_name: str
    mime_type: str
    file_size: int


class GoogleDriveAuth:
    def __init__(
        self, creds: str = "client_secrets.json", token: str = "token.json"
    ) -> None:
        self.creds = creds
        self.token = token
        self.scopes = ["https://www.googleapis.com/auth/drive.file"]

    def get_credentials(self):
        credentials = None

        if os.path.exists(self.token):
            credentials = Credentials.from_authorized_user_file(self.token, self.scopes)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.creds, self.scopes
                )
                credentials = flow.run_local_server(port=0)

            with open(self.token, "w") as token_file:
                token_file.write(credentials.to_json())

        return credentials


class GoogleDrive:
    """
    A class to interact with Google Drive for uploading and downloading files.
    This class provides asynchronous methods to initialize the Google Drive service,
    upload files, and download files. It uses `GoogleDriveAuth` for authentication
    and caches downloaded files using `alru_cache`.
    Attributes:
        auth (GoogleDriveAuth): An instance of the GoogleDriveAuth class,
                                responsible for handling authentication.
        service: The Google Drive API service object, initialized by `initialize()`.
                 It is used to make API calls to Google Drive.
    """

    def __init__(self, auth: GoogleDriveAuth) -> None:
        self.auth = auth
        self.service = None

    async def initialize(self) -> None:
        creds = self.auth.get_credentials()
        self.service = build("drive", "v3", credentials=creds)

    async def upload(self, file_bytes: bytes, filename: str, mime_type: str) -> ID:
        """
        Uploads a file to a specific Google Drive folder.
        If the service is not already initialized, this method will call `initialize()` first.
        The file is uploaded to a predefined parent folder.
        Args:
            file_bytes (bytes): The content of the file in bytes.
            filename (str): The desired name for the file in Google Drive.
            mime_type (str): The MIME type of the file (e.g., 'image/jpeg', 'application/pdf').
        Returns:
            ID: The ID of the newly uploaded file in Google Drive.
        """
        if not self.service:
            await self.initialize()
        metadata = {
            "name": filename,
            "parents": [
                "1YlVDr-04sCjML7jObb7o4TO2wvEJ5xLC",
            ],
        }
        media = MediaIoBaseUpload(
            BytesIO(file_bytes),
            mimetype=mime_type,
            resumable=False,  # Set to False for faster uploads of small files
        )

        file = (
            self.service.files() # type: ignore
            .create(body=metadata, media_body=media, fields="id")  # type: ignore
            .execute()
        )

        return file.get("id")

    @alru_cache(maxsize=50)
    async def download(self, file_id: ID) -> ImageData:
        """
        Downloads a file from Google Drive given its ID.
        If the service is not already initialized, this method will call `initialize()` first.
        The downloaded file's content, along with its metadata (filename, MIME type),
        is returned as an `Image` object. Results are cached using `alru_cache`.
        Args:
            file_id (ID): The unique ID of the file to download from Google Drive.
        Returns:
            Image: An `Image` object containing the file's ID, content (bytes),
                   filename, and MIME type.
        """
        if not self.service:
            await self.initialize()
        request = self.service.files().get_media(fileId=file_id)  # type: ignore
        fh = BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while done is False:
            _, done = downloader.next_chunk()
        fh.seek(0)
        file = self.service.files().get(fileId=file_id).execute()  # type: ignore
        filename = file.get("name")
        mime_type = file.get("mimeType")
        byte = fh.read()
        return ImageData(
            content=byte, file_name=filename, mime_type=mime_type, file_size=len(byte)
        )
