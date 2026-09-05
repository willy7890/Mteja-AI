import os 
from google_auth_oauthlib.flow import flow
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]

def create_google_flow():
    client_config = {
        "web": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        
        }
    }
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
    )
    flow.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    return flow