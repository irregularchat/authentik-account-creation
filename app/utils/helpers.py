import os
import hashlib
import base64
import requests
import pandas as pd
from cryptography.fernet import Fernet
from io import StringIO
from datetime import datetime
from config.settings import SHLINK_API_TOKEN, SHLINK_URL, LOCAL_DB, ENCRYPTION_PASSWORD, AUTHENTIK_API_URL, AUTHENTIK_API_TOKEN


# Function to shorten URL using Shlink API
def shorten_url(long_url, url_type, name=None):
    """
    Shorten a URL using Shlink API.
    
    Parameters:
        long_url (str): The URL to be shortened.
        url_type (str): The type of the URL (e.g., 'recovery', 'invite', 'setup').
        name (str, optional): The custom name for the shortened URL.
    
    Returns:
        str: The shortened URL or the original URL if the API key is not set.
    """
    if not SHLINK_API_TOKEN or not SHLINK_URL:
        return long_url  # Return original if no Shlink setup

    # Generate name for slug if not provided
    current_time = datetime.now().strftime('%d%H%M')
    if not name:
        name = f"{current_time}-{url_type}"
    else:
        name = f"{current_time}-{url_type}-{name}"

    headers = {
        'X-Api-Key': SHLINK_API_TOKEN,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    payload = {
        'longUrl': long_url,
        'customSlug': name,
        'findIfExists': True  # Reuse existing short URL if available
    }

    try:
        response = requests.post(SHLINK_URL, json=payload, headers=headers)
        response_data = response.json()

        if response.status_code in [201, 200]:
            short_url = response_data.get('shortUrl')
            if short_url:
                return short_url.replace('http://', 'https://')  # Ensure HTTPS
            else:
                print('Error: API response missing "shortUrl".')
                return long_url
        else:
            print(f'Error: {response.status_code}')
            print(response_data)
            return long_url
    except requests.exceptions.RequestException as e:
        print(f'Exception: {e}')
        return long_url


# Function to encrypt data
def encrypt_data(data):
    """
    Encrypts data using the provided encryption password.
    
    Parameters:
        data (str): The data to be encrypted.
    
    Returns:
        str: The encrypted data as a base64 encoded string.
    """
    f = Fernet(ENCRYPTION_PASSWORD)
    return f.encrypt(data.encode()).decode()


# Function to decrypt data
def decrypt_data(data):
    """
    Decrypts data using the provided encryption password.
    
    Parameters:
        data (str): The encrypted data as a base64 encoded string.
    
    Returns:
        str: The decrypted data as a string.
    """
    f = Fernet(ENCRYPTION_PASSWORD)
    return f.decrypt(data.encode()).decode()


# Function to update the local user database
def update_LOCAL_DB():
    """
    Updates the local user database by fetching users from Authentik and saving them to an encrypted CSV file.
    """
    users = list_users(AUTHENTIK_API_URL, {"Authorization": f"Bearer {AUTHENTIK_API_TOKEN}"})
    df = pd.DataFrame(users)
    encrypted_data = encrypt_data(df.to_csv(index=False))
    with open(LOCAL_DB, 'w') as file:
        file.write(encrypted_data)


# Function to load the local user database
def load_LOCAL_DB():
    """
    Loads the local user database from an encrypted CSV file.
    
    Returns:
        pd.DataFrame: The decrypted user data in a pandas DataFrame.
    """
    if not os.path.exists(LOCAL_DB):
        update_LOCAL_DB()
    with open(LOCAL_DB, 'r') as file:
        encrypted_data = file.read()
    decrypted_data = decrypt_data(encrypted_data)
    df = pd.read_csv(StringIO(decrypted_data))
    return df


# Function to search the local user database for a specific username
def search_LOCAL_DB(username):
    """
    Searches for a username in the local user database.
    
    Parameters:
        username (str): The username to search for.
    
    Returns:
        pd.DataFrame: The user data matching the username.
    """
    df = load_LOCAL_DB()
    return df[df['username'].str.lower() == username.lower()]


# Helper function to create a base username from first and last name
def get_base_username(first_name, last_name):
    """
    Creates a base username from the first and last name.
    
    Parameters:
        first_name (str): The user's first name.
        last_name (str): The user's last name.
    
    Returns:
        str: The generated base username.
    """
    if first_name and last_name:
        return f"{first_name.strip().lower()}-{last_name.strip()[0].lower()}"
    elif first_name:
        return first_name.strip().lower()
    elif last_name:
        return last_name.strip().lower()
    else:
        return "pending"


# Helper function to create a unique username if the base one exists
def create_unique_username(base_username, existing_usernames):
    """
    Creates a unique username by appending a number if the base username already exists.
    
    Parameters:
        base_username (str): The base username to start with.
        existing_usernames (set): A set of existing usernames to check against.
    
    Returns:
        str: A unique username that does not exist in the provided set.
    """
    counter = 1
    new_username = base_username
    while new_username in existing_usernames:
        new_username = f"{base_username}{counter}"
        counter += 1
    return new_username


# Function to get existing usernames from Authentik
def get_existing_usernames(api_url, headers):
    """
    Fetches a set of existing usernames from Authentik.
    
    Parameters:
        api_url (str): The Authentik API URL.
        headers (dict): The request headers with authentication.
    
    Returns:
        set: A set of existing usernames.
    """
    url = f"{api_url}/core/users/"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    users = response.json()['results']
    return {user['username'] for user in users}