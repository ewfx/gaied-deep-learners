import requests
import json
from msal import PublicClientApplication

CLIENT_ID = ""  # Replace with your Azure App ID
TENANT_ID = "consumers"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["User.Read", "Mail.Read"]
GRAPH_API_URL = "https://graph.microsoft.com/v1.0/me/messages"


def authenticate():
    app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
    flow = app.initiate_device_flow(scopes=SCOPES)
    print(f"Go to {flow['verification_uri']} and enter the code: {flow['user_code']} to authenticate.")
    return app.acquire_token_by_device_flow(flow)


def fetch_emails_with_attachments():
    result = authenticate()
    if "access_token" not in result:
        print("Authentication failed!")
        return []

    headers = {"Authorization": f"Bearer {result['access_token']}"}
    filter_query = "?$filter=startswith(subject, 'hiring')"
    response = requests.get(GRAPH_API_URL + filter_query, headers=headers)
    if response.status_code != 200:
        print("Error fetching emails:", response.text)
        return []

    emails = response.json().get("value", [])
    return [{
        "subject": email['subject'],
        "bodyPreview": email['bodyPreview'],
        "attachments": fetch_attachments(email['id'], headers)
    } for email in emails]


def fetch_attachments(email_id, headers):
    attachments_url = f"{GRAPH_API_URL}/{email_id}/attachments"
    response = requests.get(attachments_url, headers=headers)
    if response.status_code != 200:
        return []

    return response.json().get("value", [])
