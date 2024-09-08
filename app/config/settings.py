import os
from dotenv import load_dotenv

load_dotenv()

AUTHENTIK_API_TOKEN = os.getenv("AUTHENTIK_API_TOKEN")
AUTHENTIK_API_URL = os.getenv("AUTHENTIK_API_URL")
MAIN_GROUP_ID = os.getenv("MAIN_GROUP_ID")
BASE_DOMAIN = os.getenv("BASE_DOMAIN")
SHLINK_API_TOKEN = os.getenv("SHLINK_API_TOKEN")
SHLINK_URL = os.getenv("SHLINK_URL")