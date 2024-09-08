#home.py
import streamlit as st
from auth.api import create_user, list_users, generate_recovery_link, create_invite
from utils.helpers import shorten_url, update_LOCAL_DB, search_LOCAL_DB, get_existing_usernames, create_unique_username
from config.settings import AUTHENTIK_API_URL, BASE_DOMAIN, MAIN_GROUP_ID, AUTHENTIK_API_TOKEN, FLOW_ID
from datetime import datetime, timedelta
from pytz import timezone

# In app/ui/home.py, inside the render_home_page function

# Function to generate a base username from first and last name
def get_base_username(first_name, last_name):
    """
    Generates a base username from the first and last name.
    
    Parameters:
        first_name (str): The user's first name.
        last_name (str): The user's last name.
    
    Returns:
        str: The base username.
    """
    if first_name and last_name:
        return f"{first_name.strip().lower()}-{last_name.strip()[0].lower()}"
    elif first_name:
        return first_name.strip().lower()
    elif last_name:
        return last_name.strip().lower()
    else:
        return "pending"


# Main function to render the home page UI
def render_home_page():
    eastern = timezone('US/Eastern')

    # Display links on the left side and form on the right side
    col_links, col_form = st.columns([2, 1])

    with col_links:
        st.markdown("""
        - [Login to the IrregularChat SSO](https://sso.irregularchat.com)
        - [📋 Use the Signal CopyPasta for Welcome Messages](https://wiki.irregularchat.com/en/community/chat/admin/signal-prompts)
        - [Admin Prompts for Common Situations](https://wiki.irregularchat.com/community/chat/admin.md)
        - [🔗 Links to All the Community Chats and Services](https://wiki.irregularchat.com/community/links.md)
        """)

    # First name and last name input for dynamic username generation
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("Enter First Name")
    with col2:
        last_name = st.text_input("Enter Last Name")

    base_username = get_base_username(first_name, last_name)
    st.session_state['username_input'] = base_username


    # Username input and operation selection
    username_input = st.text_input("Username", key="username_input")
    operation = st.selectbox("Select Operation", [
        "Create User", 
        "Generate Recovery Link", 
        "Create Invite",
        "List Users"
    ])

    # Email and invited by inputs
    col1, col2 = st.columns(2)
    with col1:
        email_input = st.text_input("Enter Email Address")
    with col2:
        invited_by = st.text_input("Invited by")

    # Date and time inputs for operations requiring expiration time (e.g., invite generation)
    if operation in ["Generate Recovery Link", "Create Invite"]:
        expires_default = datetime.now() + timedelta(hours=2)
        expires_date = st.date_input("Expiration Date (optional)", value=expires_default.date())
        expires_time = st.time_input("Expiration Time (optional)", value=expires_default.time())
    else:
        expires_date, expires_time = None, None

    # Submit button
    submit_button = st.button("Submit")

    # Handle form submission
    if submit_button:
        handle_form_submission(operation, username_input, email_input, first_name, last_name, invited_by, expires_date, expires_time)


# Function to handle form submission based on the selected operation
def handle_form_submission(operation, username_input, email_input, first_name, last_name, invited_by, expires_date=None, expires_time=None):
    eastern = timezone('US/Eastern')
    headers = {"Authorization": f"Bearer {AUTHENTIK_API_TOKEN}", "Content-Type": "application/json"}

    try:
        if operation == "Create User":
            # Update local database and check if the user exists
            update_LOCAL_DB()
            user_exists = search_LOCAL_DB(username_input)
            if not user_exists.empty:
                st.warning(f"User {username_input} already exists. Creating a unique username.")
                existing_usernames = get_existing_usernames(AUTHENTIK_API_URL, headers)
                new_username = create_unique_username(username_input, existing_usernames)
            else:
                existing_usernames = get_existing_usernames(AUTHENTIK_API_URL, headers)
                new_username = create_unique_username(username_input, existing_usernames)
            
            email = email_input or f"{new_username}@{BASE_DOMAIN}"
            full_name = f"{first_name.strip()} {last_name.strip()}"
            new_user = create_user(AUTHENTIK_API_URL, headers, new_username, email, full_name)

            if new_user:
                shortened_recovery_link = shorten_url(generate_recovery_link(AUTHENTIK_API_URL, headers, new_username), 'first-login', f"{new_username}")
                st.success(f"User {new_username} created successfully! Recovery link: {shortened_recovery_link}")
            else:
                st.error(f"Could not create user {new_username}. Please try again.")

        elif operation == "Generate Recovery Link":
            recovery_link = generate_recovery_link(AUTHENTIK_API_URL, headers, username_input)
            st.success(f"Recovery link for {username_input}: {recovery_link}")

        elif operation == "Create Invite":
            if expires_date and expires_time:
                expires = datetime.combine(expires_date, expires_time).isoformat()
            else:
                expires = None
            invite_link, invite_expires = create_invite(headers, username_input, expires)
            if invite_link:
                st.success(f"Invite link: {invite_link}")
            else:
                st.error("Invite creation failed.")

        elif operation == "List Users":
            users = list_users(AUTHENTIK_API_URL, headers, username_input if username_input else None)
            
            if users:
                # Convert the user data to a DataFrame for better presentation
                df = pd.DataFrame(users)
                
                # Selecting only relevant columns to display
                df = df[['username', 'email', 'is_active', 'last_login']]  # Add other columns as necessary
                
                # Display the table with Streamlit
                st.dataframe(df)
                
                # Optionally, you can provide download functionality for users
                st.download_button("Download User Data", data=df.to_csv(), file_name="users.csv")
            else:
                st.warning("No users found")

    except Exception as e:
        st.error(f"An error occurred: {e}")