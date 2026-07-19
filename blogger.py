from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from config import BLOG_ID

def publish_post(title, content, credentials):
    service = build("blogger", "v3", credentials=credentials)

    post = {
        "kind": "blogger#post",
        "title": title,
        "content": content
    }

    return service.posts().insert(
        blogId=BLOG_ID,
        body=post,
        isDraft=False
    ).execute()
