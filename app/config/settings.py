#settings.py
from dotenv import load_dotenv
import os
import hashlib
import base64
from cryptography.fernet import Fernet

# Load environment variables from .env file
load_dotenv()

# Define the vars for the app from the .env file
PAGE_TITLE = os.getenv("PAGE_TITLE")
FAVICON_URL = os.getenv("FAVICON_URL")
AUTHENTIK_API_TOKEN = os.getenv("AUTHENTIK_API_TOKEN")
MAIN_GROUP_ID = os.getenv("MAIN_GROUP_ID")
BASE_DOMAIN = os.getenv("BASE_DOMAIN")
FLOW_ID = os.getenv("FLOW_ID")
LOCAL_DB = "users.csv"
ENCRYPTION_PASSWORD = base64.urlsafe_b64encode(hashlib.sha256(os.getenv("ENCRYPTION_PASSWORD").encode()).digest())
SHLINK_API_TOKEN = os.getenv("SHLINK_API_TOKEN")
SHLINK_URL = os.getenv("SHLINK_URL")
AUTHENTIK_API_URL = os.getenv("AUTHENTIK_API_URL")

