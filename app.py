import streamlit as st
from modules.load_env import load_environment_variables
from modules.ui import display_ui
from modules.authentik import AuthentikAPI
from modules.shlink import shorten_url
from modules.database import load_local_db, update_local_db, search_local_db
from modules.user_management import (
    create_user,
    generate_recovery_link,
    create_invite,
    get_existing_usernames,
    create_unique_username,
    list_users,
    update_user_status,
    delete_user,
    reset_user_password,
)
from datetime import datetime, timedelta
from pytz import timezone
import pandas as pd

# Load environment variables
env_vars = load_environment_variables()

# Define the Eastern Time zone
eastern = timezone('US/Eastern')
current_time_eastern = datetime.now(eastern)
st.set_page_config(page_title=env_vars["PAGE_TITLE"], page_icon=env_vars["FAVICON_URL"])
st.title(env_vars["PAGE_TITLE"])

# Initialize the AuthentikAPI instance
authentik_api = AuthentikAPI(env_vars["AUTHENTIK_API_URL"], {
    "Authorization": f"Bearer {env_vars['AUTHENTIK_API_TOKEN']}",
    "Content-Type": "application/json"
})

# Display UI
display_ui()

# Streamlit Interface logic
operation = st.selectbox("Select Operation", [
    "Create User", 
    "Generate Recovery Link", 
    "Create Invite",
    "List Users"
])

# Local database and encryption key from environment variables
local_db = env_vars["LOCAL_DB"]
encryption_key = env_vars["ENCRYPTION_KEY"]

if operation == "Create User":
    first_name = st.text_input("Enter First Name")
    last_name = st.text_input("Enter Last Name")
    email_input = st.text_input("Enter Email Address (optional)")

    # Handle cases where first or last name might be empty
    if first_name and last_name:
        base_username = f"{first_name.strip().lower()}-{last_name.strip()[0].lower()}"
    elif first_name:
        base_username = first_name.strip().lower()
    elif last_name:
        base_username = last_name.strip().lower()
    else:
        base_username = "user"  # Default base username if both are empty

    processed_username = base_username.replace(" ", "-")
    username_input = st.text_input("Username", value=processed_username)

    if st.button("Submit"):
        try:
            # Update local database and check for existing user
            update_local_db(authentik_api, local_db, encryption_key)
            user_exists = search_local_db(username_input, local_db, encryption_key)
            if not user_exists.empty:
                st.warning(f"User {username_input} already exists. Trying to create a unique username.")
                existing_usernames = get_existing_usernames(authentik_api)
                new_username = create_unique_username(username_input, existing_usernames)
            else:
                new_username = username_input
            
            email = email_input if email_input else f"{new_username}@{env_vars['BASE_DOMAIN']}"
            full_name = f"{first_name.strip()} {last_name.strip()}"
            new_user_id = create_user(authentik_api, new_username, email, full_name, env_vars["MAIN_GROUP_ID"])
            
            if new_user_id is None:
                st.warning(f"Username {new_username} might already exist. Please try again.")
            else:
                # Generate and shorten the setup link
                setup_link = f"https://{env_vars['BASE_DOMAIN']}/setup/{new_username}"
                setup_link = shorten_url(setup_link, 'setup', f"{new_username}")
                                
                welcome_message = f"""
                🌟 Welcome to the IrregularChat Community of Interest (CoI)! 🌟
                You've just joined a community focused on breaking down silos, fostering innovation, and supporting service members and veterans. Here's what you need to know to get started and a guide to join the wiki and other services:
                ---
                See Below for username ⬇️
                Username: {new_username}
                👆🏼 See Above for username 👆🏼

                1️⃣ Step 1:
                - Activate your IrregularChat Login with your username 👉🏼 {new_username} 👈🏼 here: {setup_link}

                2️⃣ Step 2:
                - Login to the wiki with that Irregular Chat Login and visit https://url.irregular.chat/welcome
                """
                st.code(welcome_message, language='markdown')
                st.session_state['message'] = welcome_message
                update_local_db(authentik_api, local_db, encryption_key)
                st.session_state['user_list'] = None  # Clear user list if there was any
                st.success("User created successfully!")

        except Exception as e:
            st.error(f"An error occurred: {e}")

elif operation == "Generate Recovery Link":
    username_input = st.text_input("Enter Username")

    if st.button("Generate Recovery Link"):
        try:
            recovery_link = generate_recovery_link(authentik_api, username_input)
            recovery_message = f"""
            🌟 Your account recovery link 🌟
            **Username**: {username_input}
            **Recovery Link**: {recovery_link}

            Use the link above to recover your account.
            """
            st.code(recovery_message, language='markdown')
            st.session_state['message'] = recovery_message
            st.session_state['user_list'] = None  # Clear user list if there was any
            st.success("Recovery link generated successfully!")
        except Exception as e:
            st.error(f"An error occurred: {e}")

elif operation == "Create Invite":
    name_input = st.text_input("Enter Name for Invite")
    expires_default = datetime.now() + timedelta(hours=2)
    expires_date = st.date_input("Enter Expiration Date (optional)", value=expires_default.date())
    expires_time = st.time_input("Enter Expiration Time (optional)", value=expires_default.time())

    if st.button("Create Invite"):
        try:
            expires = None
            if expires_date and expires_time:
                local_expires = datetime.combine(expires_date, expires_time)
                expires = local_expires.isoformat()
            invite_link, invite_expires = create_invite(authentik_api, name_input, env_vars["FLOW_ID"], expires)

            if invite_expires:
                invite_expires_time = datetime.fromisoformat(invite_expires.replace('Z', '+00:00')).astimezone(timezone('US/Eastern')) - datetime.now(timezone('US/Eastern'))
                hours, remainder = divmod(invite_expires_time.total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)
                invite_message = f"""
                💣 This Invite Will Self Destruct! ⏳
                This is how you get an IrregularChat Login and how you can see all the chats and services:
                
                IrregularChat Temp Invite ⏭️ : {invite_link}
                ⏲️ Invite Expires: {int(hours)} hours and {int(minutes)} minutes from now
                
                🌟 After you login you'll see options for the wiki, the forum, matrix "element messenger", and other self-hosted services. 
                Login to the wiki with that Irregular Chat Login and visit https://url.irregular.chat/welcome/
                """
                st.code(invite_message, language='markdown')
                st.session_state['user_list'] = None
                st.success("Invite created successfully!")
            else:
                st.error("Invite creation failed.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

elif operation == "List Users":
    username_input = st.text_input("Enter Username to Search (optional)")
    
    if st.button("List Users"):
        try:
            users = list_users(authentik_api, username_input if username_input else None)
            st.session_state['user_list'] = users
            st.session_state['message'] = "Users listed successfully!"
        except Exception as e:
            st.error(f"An error occurred: {e}")

if 'message' in st.session_state:
    st.success(st.session_state['message'])

if 'user_list' in st.session_state and st.session_state['user_list']:
    df = pd.DataFrame(st.session_state['user_list'])

    # Sorting options
    sort_by = st.selectbox("Sort by", options=["username", "email", "is_active"], index=0)
    sort_ascending = st.radio("Sort order", ("Ascending", "Descending"))
    df = df.sort_values(by=sort_by, ascending=(sort_ascending == "Ascending"))

    selected_users = []
    for idx, row in df.iterrows():
        if st.checkbox(f"**Username**: {row['username']}, **Email**: {row['email']}, **Active**: {row['is_active']}", key=row['username']):
            selected_users.append(row)

    st.write(f"Selected Users: {len(selected_users)}")

    if selected_users:
        st.write("**Actions for Selected Users**")
        action = st.selectbox("Select Action", ["Activate", "Deactivate", "Reset Password", "Delete"])

        if action == "Reset Password":
            new_password = st.text_input("Enter new password", type="password")

        if st.button("Apply"):
            try:
                for user in selected_users:
                    user_id = user['pk']
                    if action == "Activate":
                        update_user_status(authentik_api, user_id, True)
                    elif action == "Deactivate":
                        update_user_status(authentik_api, user_id, False)
                    elif action == "Reset Password":
                        if new_password:
                            reset_user_password(authentik_api, user_id, new_password)
                        else:
                            st.warning("Please enter a new password")
                            break
                    elif action == "Delete":
                        delete_user(authentik_api, user_id)
                st.success(f"{action} action applied successfully to selected users.")
            except Exception as e:
                st.error(f"An error occurred while applying {action} action: {e}")

    st.dataframe(df)

if 'message' in st.session_state:
    del st.session_state['message']