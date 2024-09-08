import requests
from datetime import datetime
from pytz import timezone

def shorten_url(long_url, type, name=None, shlink_url=None, shlink_api_token=None):
    """
    Shorten a URL using the Shlink API.

    Parameters:
        long_url (str): The URL to be shortened.
        type (str): The type of the URL (e.g., 'recovery', 'invite', 'setup').
        name (str, optional): The custom name for the shortened URL. Defaults to 'DDHHMM-type-name'.
        shlink_url (str, optional): The base URL for the Shlink API.
        shlink_api_token (str, optional): The API token for Shlink.

    Returns:
        str: The shortened URL or the original URL if the API key is not set.
    """
    if not shlink_api_token or not shlink_url:
        return long_url

    eastern = timezone('US/Eastern')
    current_time_eastern = datetime.now(eastern)

    if not name:
        name = f"{current_time_eastern.strftime('%d%H%M')}-{type}"
    else:
        name = f"{current_time_eastern.strftime('%d%H%M')}-{type}-{name}"

    headers = {
        'X-Api-Key': shlink_api_token,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    payload = {
        'longUrl': long_url,
        'customSlug': name,
        'findIfExists': True
    }

    try:
        response = requests.post(shlink_url, json=payload, headers=headers)
        response_data = response.json()

        if response.status_code in [200, 201]:
            short_url = response_data.get('shortUrl')
            if short_url:
                return short_url.replace('http://', 'https://')
            else:
                return long_url
        else:
            return long_url
    except requests.exceptions.RequestException:
        return long_url