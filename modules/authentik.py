import requests

class AuthentikAPI:
    def __init__(self, api_url, headers):
        self.api_url = api_url
        self.headers = headers

    def get_user_id_by_username(self, username):
        """
        Retrieve the user ID for a given username from the Authentik API.

        Parameters:
            username (str): The username to search for.

        Returns:
            int: The user ID if found.

        Raises:
            ValueError: If no user is found with the given username.
        """
        url = f"{self.api_url}/core/users/?search={username}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        users = response.json().get('results', [])
        if not users:
            raise ValueError(f"User with username {username} not found.")
        return users[0]['pk']

    def list_users(self, search_term=None):
        """
        List all users or search for users by a term.

        Parameters:
            search_term (str, optional): A term to search users by. Defaults to None.

        Returns:
            list: A list of users matching the search term.
        """
        url = f"{self.api_url}/core/users/"
        if search_term:
            url += f"?search={search_term}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json().get('results', [])

    def create_user(self, username, email, name, group_id):
        """
        Create a new user in Authentik.

        Parameters:
            username (str): The username for the new user.
            email (str): The email address for the new user.
            name (str): The full name of the new user.
            group_id (str): The group ID to assign the user to.

        Returns:
            int: The user ID of the newly created user.

        Raises:
            Exception: If user creation fails.
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
        url = f"{self.api_url}/core/users/"
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 400:
            return None
        response.raise_for_status()
        return response.json()['pk']

    def update_user_status(self, user_id, is_active):
        """
        Update the active status of a user.

        Parameters:
            user_id (int): The user ID to update.
            is_active (bool): Whether the user should be active.

        Returns:
            dict: The updated user information.
        """
        url = f"{self.api_url}/core/users/{user_id}/"
        data = {"is_active": is_active}
        response = requests.patch(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def delete_user(self, user_id):
        """
        Delete a user by their user ID.

        Parameters:
            user_id (int): The ID of the user to delete.

        Returns:
            bool: True if the user was deleted successfully, False otherwise.
        """
        url = f"{self.api_url}/core/users/{user_id}/"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return response.status_code == 204

    def reset_user_password(self, user_id, new_password):
        """
        Reset the password of a user.

        Parameters:
            user_id (int): The ID of the user whose password is to be reset.
            new_password (str): The new password to set.

        Returns:
            dict: The response from the password reset operation.
        """
        url = f"{self.api_url}/core/users/{user_id}/set_password/"
        data = {"password": new_password}
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()