import requests

def create_user(api_url, token, username, email):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"username": username, "email": email, "groups": [MAIN_GROUP_ID]}
    
    response = requests.post(f"{api_url}/core/users/", headers=headers, json=data)
    return response.json()

def list_users(api_url, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{api_url}/core/users/", headers=headers)
    return response.json()