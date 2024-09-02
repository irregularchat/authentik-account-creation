import requests
from datetime import datetime
from pytz import timezone
import os

# Load the environment variables or configuration globally
SHLINK_API_TOKEN = os.getenv("SHLINK_API_TOKEN")
SHLINK_URL = os.getenv("SHLINK_URL")

def shorten_url(long_url, type, name=None):
    """
    Shorten a URL using Shlink API.
    
    Parameters:
        long_url (str): The URL to be shortened.
        type (str): The type of the URL (e.g., 'recovery', 'invite', 'setup').
        name (str, optional): The custom name for the shortened URL. Defaults to 'DDHHMM-type-name'.
    
    Returns:
        str: The shortened URL or the original URL if the API key is not set.
    """
    eastern = timezone('US/Eastern')
    current_time_eastern = datetime.now(eastern)

    if not SHLINK_API_TOKEN or SHLINK_API_TOKEN == "your_api_token_here" or not SHLINK_URL:
        return long_url

    if not name:
        name = f"{current_time_eastern.strftime('%d%H%M')}-{type}"
    else:
        name = f"{current_time_eastern.strftime('%d%H%M')}-{type}-{name}"

    headers = {
        'X-Api-Key': SHLINK_API_TOKEN,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    payload = {
        'longUrl': long_url,
        'customSlug': name,
        'findIfExists': True  # Optional: reuse an existing short URL if the long URL was previously shortened
    }

    try:
        response = requests.post(SHLINK_URL, json=payload, headers=headers)
        response_data = response.json()

        if response.status_code in [200, 201]:
            short_url = response_data.get('shortUrl')
            if short_url:
                # change http:// to https:// to prevent mixed content issues
                return short_url.replace('http://', 'https://')
            else:
                print('Error: The API response does not contain a "shortUrl" field.')
                return long_url
        else:
            print(f'Error: {response.status_code}')
            print(response_data)
            return long_url
    except requests.exceptions.RequestException as e:
        print(f'Exception: {e}')
        return long_url