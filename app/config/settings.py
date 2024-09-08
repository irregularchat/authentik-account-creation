import os
from dotenv import load_dotenv

load_dotenv()

PAGE_TITLE = os.getenv("PAGE_TITLE")
FAVICON_URL = os.getenv("FAVICON_URL")
AUTHENTIK_API_TOKEN = os.getenv("AUTHENTIK_API_TOKEN")
AUTHENTIK_API_URL = os.getenv("AUTHENTIK_API_URL")
MAIN_GROUP_ID = os.getenv("MAIN_GROUP_ID")
BASE_DOMAIN = os.getenv("BASE_DOMAIN")
FLOW_ID = os.getenv("FLOW_ID")
ENCRYPTION_PASSWORD = base64.urlsafe_b64encode(hashlib.sha256(os.getenv("ENCRYPTION_PASSWORD").encode()).digest())
SHLINK_API_TOKEN = os.getenv("SHLINK_API_TOKEN")
SHLINK_URL = os.getenv("SHLINK_URL")