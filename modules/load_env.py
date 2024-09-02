import os
from dotenv import load_dotenv
import hashlib
import base64

def load_environment_variables():
    load_dotenv()
    
    encryption_key = base64.urlsafe_b64encode(hashlib.sha256(os.getenv("ENCRYPTION_PASSWORD").encode()).digest())
    
    return {
        "PAGE_TITLE": os.getenv("PAGE_TITLE"),
        "FAVICON_URL": os.getenv("FAVICON_URL"),
        "AUTHENTIK_API_TOKEN": os.getenv("AUTHENTIK_API_TOKEN"),
        "MAIN_GROUP_ID": os.getenv("MAIN_GROUP_ID"),
        "BASE_DOMAIN": os.getenv("BASE_DOMAIN"),
        "FLOW_ID": os.getenv("FLOW_ID"),
        "SHLINK_API_TOKEN": os.getenv("SHLINK_API_TOKEN"),
        "SHLINK_URL": os.getenv("SHLINK_URL"),
        "AUTHENTIK_API_URL": os.getenv("AUTHENTIK_API_URL"),  
        "ENCRYPTION_KEY": encryption_key ,
        "LOCAL_DB": os.getenv("LOCAL_DB", "users.csv") 
    }