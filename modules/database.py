import os
import pandas as pd
from cryptography.fernet import Fernet
from io import StringIO

def encrypt_data(data, encryption_key):
    """
    Encrypt the provided data using the given encryption key.

    Parameters:
        data (str): The data to encrypt.
        encryption_key (bytes): The encryption key.

    Returns:
        str: The encrypted data.
    """
    f = Fernet(encryption_key)
    return f.encrypt(data.encode()).decode()

def decrypt_data(data, encryption_key):
    """
    Decrypt the provided data using the given encryption key.

    Parameters:
        data (str): The data to decrypt.
        encryption_key (bytes): The encryption key.

    Returns:
        str: The decrypted data.
    """
    f = Fernet(encryption_key)
    return f.decrypt(data.encode()).decode()

def update_local_db(authentik_api, local_db, encryption_key):
    """
    Updates the local database with the latest user data from the Authentik API.

    Parameters:
        authentik_api (AuthentikAPI): An instance of the AuthentikAPI class.
        local_db (str): Path to the local database file.
        encryption_key (bytes): Encryption key for securing the local database.
    """
    users = authentik_api.list_users()
    df = pd.DataFrame(users)
    encrypted_data = encrypt_data(df.to_csv(index=False), encryption_key)
    with open(local_db, 'w') as file:
        file.write(encrypted_data)

def load_local_db(local_db, encryption_key):
    """
    Loads the local database and decrypts it.

    Parameters:
        local_db (str): Path to the local database file.
        encryption_key (bytes): Encryption key for decrypting the local database.

    Returns:
        pd.DataFrame: A DataFrame containing the decrypted user data.
    """
    if not os.path.exists(local_db):
        raise FileNotFoundError("Local database not found. Please ensure the database file exists.")
    with open(local_db, 'r') as file:
        encrypted_data = file.read()
    decrypted_data = decrypt_data(encrypted_data, encryption_key)
    return pd.read_csv(StringIO(decrypted_data))

def search_local_db(username, local_db, encryption_key):
    """
    Search for a user in the local database by username.

    Parameters:
        username (str): The username to search for.
        local_db (str): Path to the local database file.
        encryption_key (bytes): Encryption key for decrypting the local database.

    Returns:
        pd.DataFrame: A DataFrame containing the user data if found.
    """
    df = load_local_db(local_db, encryption_key)
    return df[df['username'].str.lower() == username.lower()]