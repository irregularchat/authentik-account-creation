# Authentik User Creation Script

This script automates the creation of user accounts on an Authentik instance. It generates a strong password and ensures unique usernames. The script uses environment variables for secure handling of sensitive information.

## Prerequisites

- Python 3.x
- `requests` library
- `python-dotenv` library
- Access to the Authentik API

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/irregularchat/authentik-account-creation.git
   cd authentik-user-creation
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**
   - Create a `.env` file in the project directory and add the following:
     ```env
     AUTHENTIK_API_TOKEN=your_api_token_here
     base_password=base-pass-here
     ```

## Usage

Run the script to create a new user account:
```bash
python create_user.py
```

### Example Output
```plaintext
New Username: user1
New Password: TempPassword@2gh#k
User created successfully: {user details JSON response}
```

## Script Overview

### Environment Variables

- `AUTHENTIK_API_TOKEN`: The API token for accessing the Authentik API.
- `base_password`: The base pasword to generate unique passwords.

### Functions

- **generate_password()**: Generates a strong password starting with "TempPassword" followed by a random sequence of characters and numbers.
- **create_unique_username(base_username, existing_usernames)**: Ensures the generated username is unique by appending a counter if necessary.
- **get_existing_usernames(api_url, headers)**: Retrieves the list of existing usernames from the Authentik API.
- **create_user(api_url, headers, username, password)**: Creates a new user on the Authentik instance with the provided username and password.

## Best Practices for Setting Up the Environment

1. **Use a Virtual Environment**: Always use a virtual environment to manage dependencies and avoid conflicts with other projects.
2. **Store Sensitive Information Securely**: Use environment variables to store sensitive information like API tokens. Never hard-code them in your script.
3. **Use a `.env` File**: Use a `.env` file to manage environment variables. Make sure to add the `.env` file to your `.gitignore` to avoid committing sensitive information to version control.

## Running on a Server

#TODO

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.
