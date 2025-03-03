"""Wrapper for Google OAuth2 API."""
import os
import google_auth_oauthlib.flow
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

YOUTUBE_UPLOAD_SCOPE = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]

def get_resource(client_secrets_file, credentials_file):
    """Authenticate and return a Resource object."""
    flow = InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, YOUTUBE_UPLOAD_SCOPE
    )
    credentials = flow.run_local_server(port=0)
    return build("youtube", "v3", credentials=credentials)