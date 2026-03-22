import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/fitness.activity.read']

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
        """Fetches steps for the last 24 hours."""
        creds = Credentials.from_authorized_user_info(credentials_dict, SCOPES)
        service = build('fitness', 'v1', credentials=creds)
        now = datetime.datetime.utcnow()
        start_time = now - datetime.timedelta(days=1)
        start_ns = int(start_time.timestamp() * 1e9)    # Convert to nanoseconds (required by Google Fit API)
        end_ns = int(now.timestamp() * 1e9)
        dataset_id = f"{start_ns}-{end_ns}"
        response = service.users().dataset().aggregate(userId='me', body={
            "aggregateBy": [{"dataTypeName": "com.google.step_count.delta"}],
            "bucketByTime": {"durationMillis": 86400000},   # Bucket by day (24 hours)
            "startTimeMillis": int(start_time.timestamp() * 1000),
            "endTimeMillis": int(now.timestamp() * 1000)
        }).execute()

        # try:
        #     steps = response['bucket'][0]['dataset'][0]['point'][0]['value'][0]['intVal']
        #     return steps
        # except (KeyError, IndexError):
        #     return 0

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
        return total_steps