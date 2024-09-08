import requests

class AuthentikAPI:
    def __init__(self, api_url, headers):
        self.api_url = api_url
        self.headers = headers

    def get_user_id_by_username(self, username):
        """
        Get the user ID for a given username.

        Parameters:
            username (str): The username to search for.

        Returns:
            int: The user ID of the found user.
        """
        url = f"{self.api_url}/core/users/?search={username}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        users = response.json()['results']
        if not users:
            raise ValueError(f"User with username {username} not found.")
        return users[0]['pk']

    def list_users(self, search_term=None):
        """
        List all users or search for users by a search term.

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