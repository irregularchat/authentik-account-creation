import os
from dotenv import load_dotenv
import base64

load_dotenv()

PAGE_TITLE = os.getenv("PAGE_TITLE")
FAVICON_URL = os.getenv("FAVICON_URL")
AUTHENTIK_API_TOKEN = os.getenv("AUTHENTIK_API_TOKEN")
AUTHENTIK_API_URL = os.getenv("AUTHENTIK_API_URL")
MAIN_GROUP_ID = os.getenv("MAIN_GROUP_ID")
BASE_DOMAIN = os.getenv("BASE_DOMAIN")
FLOW_ID = os.getenv("FLOW_ID")
SHLINK_API_TOKEN = os.getenv("SHLINK_API_TOKEN")
SHLINK_URL = os.getenv("SHLINK_URL")
ENCRYPTION_PASSWORD_RAW = os.getenv("ENCRYPTION_PASSWORD")
if not ENCRYPTION_PASSWORD_RAW:
    raise ValueError("ENCRYPTION_PASSWORD is not set in the environment variables")
ENCRYPTION_PASSWORD = base64.urlsafe_b64encode(hashlib.sha256(ENCRYPTION_PASSWORD_RAW.encode()).digest())
