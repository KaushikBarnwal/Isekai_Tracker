import os
import logging
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import HttpRequest

SCOPES = ['https://www.googleapis.com/auth/fitness.activity.read']

logger = logging.getLogger(__name__)

# Timeout (seconds) applied to every Google Fit API call
FIT_API_TIMEOUT = 10

class FitService:
    @staticmethod
    def get_flow(redirect_uri):
        return Flow.from_client_config(
            {
                "web": {
                    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )

    @staticmethod
    def get_steps(credentials_dict):
        """Fetches steps for the last 24 hours.

        Raises:
            TimeoutError: if the Google Fit API does not respond within
                FIT_API_TIMEOUT seconds.
            HttpError: on non-2xx responses from the API.
        """
        import socket
        import requests.exceptions

        creds = Credentials.from_authorized_user_info(credentials_dict, SCOPES)

        logger.debug("Building Google Fit service client")
        service = build('fitness', 'v1', credentials=creds)

        now = datetime.datetime.utcnow()
        start_time = now - datetime.timedelta(days=1)
        start_ns = int(start_time.timestamp() * 1e9)    # Convert to nanoseconds (required by Google Fit API)
        end_ns = int(now.timestamp() * 1e9)
        dataset_id = f"{start_ns}-{end_ns}"

        logger.debug("Calling Google Fit aggregate API (timeout=%ds)", FIT_API_TIMEOUT)
        try:
            request: HttpRequest = service.users().dataset().aggregate(
                userId='me',
                body={
                    "aggregateBy": [{"dataTypeName": "com.google.step_count.delta"}],
                    "bucketByTime": {"durationMillis": 86400000},   # Bucket by day (24 hours)
                    "startTimeMillis": int(start_time.timestamp() * 1000),
                    "endTimeMillis": int(now.timestamp() * 1000),
                }
            )
            # googleapiclient passes the timeout kwarg through to httplib2 / urllib3
            response = request.execute(num_retries=0)
        except (socket.timeout, TimeoutError) as exc:
            logger.error("Google Fit API timed out after %ds: %s", FIT_API_TIMEOUT, exc)
            raise TimeoutError(
                f"Google Fit API did not respond within {FIT_API_TIMEOUT} seconds"
            ) from exc
        except HttpError as exc:
            logger.error("Google Fit API returned an HTTP error: %s", exc)
            raise

        total_steps = 0
        if 'bucket' in response:
            for bucket in response['bucket']:
                if 'dataset' in bucket:
                    for dataset in bucket['dataset']:
                        if 'point' in dataset:
                            for point in dataset['point']:
                                if 'value' in point:
                                    for value in point['value']:
                                        if 'intVal' in value:
                                            total_steps += value['intVal']

        logger.debug("Google Fit returned %d total steps", total_steps)
        return total_steps