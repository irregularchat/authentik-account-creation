import streamlit as st
import requests
from datetime import datetime, timedelta, timezone
import json
from authlib.integrations.requests_client import OAuth2Session
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configuration
client_id = os.getenv("AUTH0_CLIENT_ID")
client_secret = os.getenv("AUTH0_CLIENT_SECRET")
authorize_url = os.getenv("AUTH0_AUTHORIZE_URL")
token_url = os.getenv("AUTH0_TOKEN_URL")
redirect_uri = os.getenv("AUTH0_CALLBACK_URL")

# Initialize Streamlit app
st.title("IrregularChat Authentik Management")

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = ""
if 'main_group_id' not in st.session_state:
    st.session_state.main_group_id = ""
if 'entity_name' not in st.session_state:
    st.session_state.entity_name = ""
if 'expires_date' not in st.session_state:
    st.session_state.expires_date = None
if 'expires_time' not in st.session_state:
    st.session_state.expires_time = None
if 'auth0_user' not in st.session_state:
    st.session_state.auth0_user = None
if 'auth_token' not in st.session_state:
    st.session_state.auth_token = None

base_domain = "irregularchat.com"  # Update this to your domain

def save_session():
    session_data = {
        "token": st.session_state.token,
        "main_group_id": st.session_state.main_group_id,
        "entity_name": st.session_state.entity_name,
        "expires_date": st.session_state.expires_date.isoformat() if st.session_state.expires_date else None,
        "expires_time": st.session_state.expires_time.isoformat() if st.session_state.expires_time else None,
        "auth0_user": st.session_state.auth0_user,
        "auth_token": st.session_state.auth_token
    }
    with open('session_data.json', 'w') as f:
        json.dump(session_data, f)
    st.success("Session details saved successfully!")

def load_session():
    try:
        with open('session_data.json', 'r') as f:
            session_data = json.load(f)
        st.session_state.token = session_data["token"]
        st.session_state.main_group_id = session_data["main_group_id"]
        st.session_state.entity_name = session_data["entity_name"]
        st.session_state.expires_date = datetime.fromisoformat(session_data["expires_date"]) if session_data["expires_date"] else None
        st.session_state.expires_time = datetime.fromisoformat(session_data["expires_time"]).time() if session_data["expires_time"] else None
        st.session_state.auth0_user = session_data["auth0_user"]
        st.session_state.auth_token = session_data["auth_token"]
        st.success("Session details loaded successfully!")
    except FileNotFoundError:
        st.error("No saved session found.")

# UI for inputs
st.text_input("Enter your AUTHENTIK API TOKEN", type="password", key="token")
st.text_input("Enter the MAIN GROUP ID", key="main_group_id")
operation = st.selectbox("Select Operation", ["Create User", "Generate Recovery Link", "Create Invite"])
st.text_input("Enter Username or Invite Name", key="entity_name")
st.date_input("Enter Expiration Date (optional)", key="expires_date")
st.time_input("Enter Expiration Time (optional)", key="expires_time")

# Buttons to save/load session
if st.button("Save Session Details"):
    save_session()

if st.button("Load Session Details"):
    load_session()

API_URL = f"https://sso.{base_domain}/api/v3/"
headers = {
    "Authorization": f"Bearer {st.session_state.token}",
    "Content-Type": "application/json"
}

########## Functions ##########
def get_user_id_by_username(API_URL, headers, username):
    url = f"{API_URL}core/users/?search={username}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    users = response.json()['results']
    if not users:
        raise ValueError(f"User with username {username} not found.")
    return users[0]['pk']

def create_invite(API_URL, headers, name, expires=None):
    current_time_str = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H-%M-%S')
    if not name:
        name = current_time_str
    else:
        name = f"{name}-{current_time_str}"
    
    if expires:
        try:
            expires = datetime.fromisoformat(expires).isoformat()
        except ValueError:
            raise ValueError("Expiration time is in the wrong format. Use YYYY-MM-DDTHH:mm:ss.uuuuuu[+HH:MM|-HH:MM|Z].")
    else:
        expires = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()

    data = {
        "name": name,
        "expires": expires,
        "fixed_data": {},
        "single_use": True,
        "flow": "41a44b0e-1d06-4551-9ec1-41bd793b6f27"
    }
    
    url = f"{API_URL}/stages/invitation/invitations/"
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 400:
        st.error(f"400 Bad Request: {response.json()}")
    response.raise_for_status()
    return response.json()['pk']

def generate_recovery_link(API_URL, headers, username):
    user_id = get_user_id_by_username(API_URL, headers, username)
    
    url = f"{API_URL}core/users/{user_id}/recovery/"
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    
    recovery_link = response.json().get('link')
    if not recovery_link:
        raise ValueError("Failed to generate recovery link.")
    
    return recovery_link

def create_unique_username(base_username, existing_usernames):
    counter = 1
    new_username = base_username
    while new_username in existing_usernames:
        new_username = f"{base_username}{counter}"
        counter += 1
    return new_username

def get_existing_usernames(API_URL, headers):
    url = f"{API_URL}core/users/"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    users = response.json()['results']
    return {user['username'] for user in users}

def create_user(API_URL, headers, username):
    data = {
        "username": username,
        "name": username,
        "is_active": True,
        "email": f"{username}@{base_domain}",
        "groups": [st.session_state.main_group_id],
        "attributes": {},
        "path": "users",
        "type": "internal"
    }
    url = f"{API_URL}core/users/"
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 400:
        return None
    response.raise_for_status()
    return response.json()['pk']

# OAuth2 login
def login():
    if 'auth0_user' in st.session_state and st.session_state.auth0_user:
        st.write(f"Logged in as {st.session_state.auth0_user['name']}")
    else:
        auth0 = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri)
        authorization_url, state = auth0.create_authorization_url(authorize_url, scope="openid profile email")
        st.write(f"redirecting to: {authorization_url}")
        st.query_params.from_dict({"state": state})
        st.markdown(f"[Login with Auth0]({authorization_url})")

# Check if we're redirected back with the authorization code
query_params = st.query_params.to_dict()
if 'code' in query_params:
    auth0 = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri)
    token = auth0.fetch_token(token_url, authorization_response=st.query_params, code=query_params['code'])
    st.session_state.auth_token = token
    user_info = auth0.get("https://sso.irregularchat.com/application/o/userinfo", token=token)
    st.session_state.auth0_user = user_info.json()

# Call the login function
login()

# Processing the operations
if st.button("Submit"):
    try:
        if operation == "Create User":
            existing_usernames = get_existing_usernames(API_URL, headers)
            new_username = create_unique_username(st.session_state.entity_name, existing_usernames)
            new_user = create_user(API_URL, headers, new_username)
            
            while new_user is None:
                new_username = create_unique_username(st.session_state.entity_name, existing_usernames)
                new_user = create_user(API_URL, headers, new_username)
            
            recovery_link = generate_recovery_link(API_URL, headers, new_username)
            welcome_message = f"""
            🌟 Welcome to the IrregularChat Community of Interest (CoI)! 🌟
            You've just joined a community focused on breaking down silos, fostering innovation, and supporting service members and veterans. Here's what you need to know to get started and a guide to join the wiki and other services:
            Username: {new_username}
            ---
            Step 1:
            - Activate your IrregularChat Login with your username ({new_username}) here: {recovery_link}
            Step 2:
            - Login to the wiki with that Irregular Chat Login and visit https://wiki.irregularchat.com/community/welcome
            """
            st.success(welcome_message)
        
        elif operation == "Generate Recovery Link":
            recovery_link = generate_recovery_link(API_URL, headers, st.session_state.entity_name)
            recovery_message = f"""
            🌟 Your account recovery link 🌟
            Username: {st.session_state.entity_name}
            Recovery Link: {recovery_link}

            Use the link above to recover your account.
            """
            st.success(recovery_message)
        
        elif operation == "Create Invite":
            invite_id = create_invite(API_URL, headers, st.session_state.entity_name, expires)
            invite_message = f"""
            🌟 Welcome to the IrregularChat Community of Interest (CoI)! 🌟
            You've just joined a community focused on breaking down silos, fostering innovation, and supporting service members and veterans. Here's what you need to know to get started and a guide to join the wiki and other services:
            IrregularChat Temp Invite: https://sso.irregularchat.com/if/flow/simple-enrollment-flow/?itoken={invite_id}
            Invite Expires: {expires if expires else '2 hours from now'}

            🌟 After you login you'll see options for the wiki, matrix "element messenger", and other self-hosted services. 
            Login to the wiki with that Irregular Chat Login and visit https://wiki.irregularchat.com/community/links/
            """
            st.success(invite_message)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
