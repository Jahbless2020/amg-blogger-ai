# Helper to create token.json (Blogger OAuth) using the installed app flow
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/blogger"]

def main():
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)
    with open("token.json", "w") as f:
        f.write(creds.to_json())
    print("token.json created. Keep it secure and place it on the server where your bot runs.")

if __name__ == "__main__":
    main()
