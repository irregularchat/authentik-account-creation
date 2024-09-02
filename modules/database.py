import os
import pandas as pd
from cryptography.fernet import Fernet
from io import StringIO

def load_local_db(local_db, encryption_key):
    if not os.path.exists(local_db):
        update_local_db()
    with open(local_db, 'r') as file:
        encrypted_data = file.read()
    decrypted_data = decrypt_data(encrypted_data, encryption_key)
    df = pd.read_csv(StringIO(decrypted_data))
    return df

def update_local_db():
    # Update your local database
    pass

def search_local_db(username):
    df = load_local_db()
    return df[df['username'].str.lower() == username.lower()]

def encrypt_data(data, encryption_key):
    f = Fernet(encryption_key)
    return f.encrypt(data.encode()).decode()

def decrypt_data(data, encryption_key):
    f = Fernet(encryption_key)
    return f.decrypt(data.encode()).decode()