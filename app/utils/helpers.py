import requests
from datetime import datetime
from config.settings import SHLINK_API_TOKEN, SHLINK_URL

def shorten_url(long_url, url_type, name=None):
    if not SHLINK_API_TOKEN or not SHLINK_URL:
        return long_url
    
    headers = {'X-Api-Key': SHLINK_API_TOKEN}
    payload = {'longUrl': long_url, 'customSlug': f"{name}-{datetime.now()}"}

    response = requests.post(SHLINK_URL, headers=headers, json=payload)
    return response.json().get("shortUrl", long_url)