from datetime import datetime, timedelta
from pytz import timezone
import requests

def create_unique_username(base_username, existing_usernames):
    """
    Generate a unique username by appending a number to the base username if it already exists.

    Parameters:
        base_username (str): The base username to start with.
        existing_usernames (set): A set of usernames that already exist.

    Returns:
        str: A unique username.
    """
    counter = 1
    new_username = base_username
    while new_username in existing_usernames:
        new_username = f"{base_username}{counter}"
        counter += 1
    return new_username

def get_existing_usernames(authentik_api):
    """
    Retrieve all existing usernames from Authentik.

    Parameters:
        authentik_api (AuthentikAPI): An instance of the AuthentikAPI class.

    Returns:
        set: A set of all existing usernames.
    """
    users = list_users(authentik_api)
    return {user['username'] for user in users}

def list_users(authentik_api, search_term=None):
    """
    List all users or search for users by a search term.

    Parameters:
        authentik_api (AuthentikAPI): An instance of the AuthentikAPI class.
        search_term (str, optional): A term to search users by. Defaults to None.

    Returns:
        list: A list of users matching the search term.
    """
    url = f"{authentik_api.api_url}/core/users/"
    if search_term:
        url += f"?search={search_term}"
    
    response = requests.get(url, headers=authentik_api.headers)
    response.raise_for_status()
    return response.json().get('results', [])

def create_user(authentik_api, username, email, name, group_id):
    """
    Create a new user in Authentik.

    Parameters:
        authentik_api (AuthentikAPI): An instance of the AuthentikAPI class.
        username (str): The username for the new user.
        email (str): The email address for the new user.
        name (str): The full name of the new user.
        group_id (str): The group ID to assign the user to.

    Returns:
        int: The user ID of the newly created user.
    """
    data = {
        "username": username,
        "name": name,
        "is_active": True,
        "email": email,
        "groups": [group_id],
        "attributes": {},
        "path": "users",
        "type": "internal"
    }
    url = f"{authentik_api.api_url}/core/users/"
    response = requests.post(url, headers=authentik_api.headers, json=data)
    if response.status_code == 400:
        return None
    response.raise_for_status()
    return response.json()['pk']

def generate_recovery_link(authentik_api, username):
    """
    Generate an account recovery link for a user.

    Parameters:
        authentik_api (AuthentikAPI): An instance of the AuthentikAPI class.
        username (str): The username of the user to generate the recovery link for.

    Returns:
        str: The generated recovery link.
    """
    user_id = authentik_api.get_user_id_by_username(username)
    url = f"{authentik_api.api_url}/core/users/{user_id}/recovery/"
    response = requests.post(url, headers=authentik_api.headers)
    response.raise_for_status()
    
    recovery_link = response.json().get('link')
    if not recovery_link:
        raise ValueError("Failed to generate recovery link.")
    
    return recovery_link

def create_invite(authentik_api, name, flow_id, expires=None):
    """
    Create an invite for a new user.

    Parameters:
        authentik_api (AuthentikAPI): An instance of the AuthentikAPI class.
        name (str): The name of the invite.
        flow_id (str): The flow ID for the invitation.
        expires (str, optional): Expiration time for the invite. Defaults to None.

    Returns:
        tuple: The shortened invite link and the expiration time.
    """
    # Get the current time in Eastern Time Zone
    eastern = timezone('US/Eastern')
    current_time_str = datetime.now(eastern).strftime('%H-%M')

    if not name:
        name = current_time_str
    if expires is None:
        expires = (datetime.now(eastern) + timedelta(hours=2)).isoformat()

    data = {
        "name": name,
        "expires": expires,
        "fixed_data": {},
        "single_use": True,
        "flow": flow_id
    }
    
    invite_api_url = f"{authentik_api.api_url}/stages/invitation/invitations/"
    
    try:
        response = requests.post(invite_api_url, headers=authentik_api.headers, json=data)
        response.raise_for_status()
        response_data = response.json()
        
        invite_id = response_data.get('pk')
        if not invite_id:
            raise ValueError("The API response does not contain a 'pk' field.")

        invite_link = f"https://{authentik_api.api_url}/if/flow/simple-enrollment-flow/?itoken={invite_id}"
        return invite_link, expires

    except requests.exceptions.HTTPError as http_err:
        raise Exception(f"HTTP error occurred: {http_err}")
    except Exception as err:
        raise Exception(f"An error occurred: {err}")

def update_user_status(authentik_api, user_id, is_active):
    """
    Update the active status of a user.

    Parameters:
        authentik_api (AuthentikAPI): An instance of the AuthentikAPI class.
        user_id (int): The user ID to update.
        is_active (bool): Whether the user should be active.

    Returns:
        dict: The updated user information.
    """
    url = f"{authentik_api.api_url}/core/users/{user_id}/"
    data = {"is_active": is_active}
    response = requests.patch(url, headers=authentik_api.headers, json=data)
    response.raise_for_status()
    return response.json()

def delete_user(authentik_api, user_id):
    """
    Delete a user by their user ID.

    Parameters:
        authentik_api (AuthentikAPI): An instance of the AuthentikAPI class.
        user_id (int): The ID of the user to delete.

    Returns:
        bool: True if the user was deleted successfully, False otherwise.
    """
    url = f"{authentik_api.api_url}/core/users/{user_id}/"
    response = requests.delete(url, headers=authentik_api.headers)
    response.raise_for_status()
    return response.status_code == 204

def reset_user_password(authentik_api, user_id, new_password):
    """
    Reset the password of a user.

    Parameters:
        authentik_api (AuthentikAPI): An instance of the AuthentikAPI class.
        user_id (int): The ID of the user whose password is to be reset.
        new_password (str): The new password to set.

    Returns:
        dict: The response from the password reset operation.
    """
    url = f"{authentik_api.api_url}/core/users/{user_id}/set_password/"
    data = {"password": new_password}
    response = requests.post(url, headers=authentik_api.headers, json=data)
    response.raise_for_status()
    return response.json()