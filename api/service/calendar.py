from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import datetime
from common.models.user import GoogleOAuth2Token
from django.conf import settings


def add_event_calendar(user, event_data):
    try:
        token = GoogleOAuth2Token.objects.get(user=user)
    except GoogleOAuth2Token.DoesNotExist:
        raise Exception("No tokens found for user")

    credentials = Credentials(
        token=token.access_token,
        refresh_token=token.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.CLIENT_ID,
        client_secret=settings.CLIENT_SECRET,
    )

    if credentials.expired and credentials.refresh_token:
        raise Exception("Token expired")
        credentials.refresh(Request())

        # Save the new access token and expiration
        token.access_token = credentials.token
        token.expires_at = datetime.datetime.now() + datetime.timedelta(seconds=credentials.expiry)
        token.save()

    # Create a Google Calendar service object
    service = build("calendar", "v3", credentials=credentials)

    # Create a new event of the user's calendar
    created_event = service.events().insert(calendarId="primary", body=event_data).execute()
    return created_event
