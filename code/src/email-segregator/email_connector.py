import requests
import json
from msal import PublicClientApplication

# 🔹 Replace these with your Azure App credentials
CLIENT_ID = ""  # From Azure App Registration
TENANT_ID = "consumers"  # Use "consumers" for personal Outlook accounts
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["User.Read", "Mail.Read"]

# 🔹 Microsoft Graph API Endpoints
GRAPH_API_URL = "https://graph.microsoft.com/v1.0/me/messages"

# 🔹 Initialize the MSAL authentication app
app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY)

# 🔹 Get device login URL (for personal Outlook accounts)
flow = app.initiate_device_flow(scopes=SCOPES)
print("Device Flow Response:", flow)  # Debugging step

if "user_code" not in flow:
    raise Exception("Failed to create device flow. Check Client ID, Tenant ID, and Scopes.")
if "user_code" not in flow:
    raise Exception("Failed to create device flow")

print(f"Go to {flow['verification_uri']} and enter the code: {flow['user_code']} to authenticate.")
result = app.acquire_token_by_device_flow(flow)

# 🔹 Check if authentication was successful
if "access_token" in result:
    headers = {"Authorization": f"Bearer {result['access_token']}"}

    # 🔹 Filter emails where the subject contains "Turing"
    filter_query = "?$filter=startswith(subject, 'Welcome to your new Outlook.com account')"
    response = requests.get(GRAPH_API_URL + filter_query, headers=headers)

    if response.status_code == 200:
        emails = response.json().get("value", [])

        if not emails:
            print("No emails found with subject containing 'Welcome to your new Outlook.com account'.")
        else:
            print("\n🔹 Emails with Subject 'Welcome to your new Outlook.com account'':\n")
            for email in emails:
                print(f"📩 Subject: {email['subject']}")
                print(f"👤 From: {email['from']['emailAddress']['name']} <{email['from']['emailAddress']['address']}>")
                print(f"📅 Received: {email['receivedDateTime']}")
                print(f"✉ Preview: {email['bodyPreview'][:200]}")
                print("-" * 50)
    else:
        print("Error fetching emails:", response.text)
else:
    print("Authentication failed!")
