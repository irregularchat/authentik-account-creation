import requests
import logging

# Function to create a new user
def create_user(api_url, token, username, email, name, group_id, intro=None, invited_by=None):
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "username": username,
        "name": name,
        "is_active": True,
        "email": email,
        "groups": [group_id],
        "attributes": {
            "intro": intro,
            "invited_by": invited_by
        },
        "path": "users",
        "type": "internal"
    }
    url = f"{api_url}/core/users/"
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 400:
        return None
    response.raise_for_status()
    return response.json()['pk']


# Function to list users
def list_users(api_url, token, search_term=None):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{api_url}/core/users/?search={search_term}" if search_term else f"{api_url}/core/users/"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['results']


# Function to generate a recovery link for the user
def generate_recovery_link(api_url, token, username):
    # Get the user ID by username
    user_id = get_user_id_by_username(api_url, token, username)
    
    # Define the URL for generating a recovery link
    url = f"{api_url}/core/users/{user_id}/recovery/"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Make a POST request to generate the recovery link
    response = requests.post(url, headers=headers)
    response.raise_for_status()

    # Fetch the recovery link directly from the response
    recovery_link = response.json().get('link')
    
    if not recovery_link:
        raise ValueError("Failed to generate recovery link.")
    
    return recovery_link


# Function to get user ID by username
def get_user_id_by_username(api_url, token, username):
    url = f"{api_url}/core/users/?search={username}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    users = response.json()['results']
    if not users:
        raise ValueError(f"User with username {username} not found.")
    return users[0]['pk']


# Function to create an invite
def create_invite(api_url, token, flow_id, label, expires=None):
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": label,
        "expires": expires,
        "fixed_data": {},
        "single_use": True,
        "flow": flow_id
    }
    
    # Authentik API invitation endpoint
    invite_api_url = f"{api_url}/stages/invitation/invitations/"
    
    try:
        response = requests.post(invite_api_url, headers=headers, json=data)
        response.raise_for_status()
        response_data = response.json()

        # Get the invite ID and construct the full URL
        invite_id = response_data.get('pk')
        if not invite_id:
            raise ValueError("API response missing 'pk' field.")
        
        return invite_id
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        logging.info("API Response: %s", response.json())
        return None
    except Exception as err:
        logging.error(f"An error occurred: {err}")
        return None


# Function to update a user's status (activate/deactivate)
def update_user_status(api_url, token, user_id, is_active):
    url = f"{api_url}/core/users/{user_id}/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"is_active": is_active}
    
    response = requests.patch(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


# Function to delete a user
def delete_user(api_url, token, user_id):
    url = f"{api_url}/core/users/{user_id}/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.delete(url, headers=headers)
    response.raise_for_status()
    return response.status_code == 204


# Function to reset a user's password
def reset_user_password(api_url, token, user_id, new_password):
    url = f"{api_url}/core/users/{user_id}/set_password/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"password": new_password}
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()