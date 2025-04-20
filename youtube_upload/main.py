from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import pickle
import argparse
from pathlib import Path

class YouTubeUploader:
    SCOPES = [
        'https://www.googleapis.com/auth/youtube.upload',
        'https://www.googleapis.com/auth/youtube'
    ]

    def __init__(self, client_secrets_file):
        self.client_secrets_file = client_secrets_file
        self.credentials = None
        self.youtube = None

    def authenticate(self):
        """Handle OAuth2 authentication flow."""
        creds = None
        token_file = 'token.pickle'

        # Load existing credentials if available
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)

        # Refresh credentials if expired
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        # Generate new credentials if none exist
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.client_secrets_file, self.SCOPES)
            creds = flow.run_local_server(port=0)

            # Save credentials for future use
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)

        self.credentials = creds
        self.youtube = build('youtube', 'v3', credentials=creds)

    def upload_video(self, video_path, title, description='', privacy_status='private', publish_at=None,
                    tags=None, category='22'):
        """Upload a video to YouTube."""
        if not self.youtube:
            raise ValueError("Not authenticated. Call authenticate() first.")

        tags = tags or []
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category
            },
            'status': {
                "privacyStatus": ("private" if publish_at else privacy_status),
                "publishAt": publish_at,
                'selfDeclaredMadeForKids': False
            }
        }

        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Create the video upload request
        insert_request = self.youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=MediaFileUpload(
                str(video_path),
                chunksize=1024*1024,
                resumable=True
            )
        )

        # Execute the upload with progress monitoring
        response = None
        while response is None:
            try:
                status, response = insert_request.next_chunk()
                if status:
                    print(f"Uploaded {int(status.progress() * 100)}%")
            except Exception as e:
                print(f"An error occurred: {e}")
                break

        if response:
            print(f"Upload Complete! Video ID: {response['id']}")
            return response['id']
        return None

def main():
    parser = argparse.ArgumentParser(description='Upload a video to YouTube')
    parser.add_argument('--video', required=True, help='Path to video file')
    parser.add_argument('--publish-at', required=True, help='Publish Date (ISO 8601)')
    parser.add_argument('--title', required=True, help='Video title')
    parser.add_argument('--description', default='', help='Video description')
    parser.add_argument('--privacy', default='private',
                       choices=['private', 'unlisted', 'public'],
                       help='Privacy status')
    parser.add_argument('--tags', help='Comma-separated tags')
    parser.add_argument('--client-secrets', required=True,
                       help='Path to client secrets JSON file')

    args = parser.parse_args()

    uploader = YouTubeUploader(args.client_secrets)
    uploader.authenticate()

    tags = [tag.strip() for tag in args.tags.split(',')] if args.tags else []

    video_id = uploader.upload_video(
        args.video,
        args.title,
        description=args.description,
        privacy_status=args.privacy,
        publish_at=args.publish_at,
        tags=tags
    )

    if video_id:
        print(f"Video URL: https://www.youtube.com/watch?v={video_id}")

if __name__ == '__main__':
    main()
