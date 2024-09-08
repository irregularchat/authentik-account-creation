import streamlit as st
from auth.api import create_user, list_users, generate_recovery_link, create_invite
from utils.helpers import shorten_url, encrypt_data, decrypt_data, update_LOCAL_DB, search_LOCAL_DB, get_existing_usernames, create_unique_username
from config.settings import AUTHENTIK_API_URL, BASE_DOMAIN, MAIN_GROUP_ID, AUTHENTIK_API_TOKEN, FLOW_ID

def render_home_page():
    col_links, col_form = st.columns([2, 1])

    with col_links:
        st.markdown("""
        - [Login to the IrregularChat SSO](https://sso.irregularchat.com)
        - [📋 Use the Signal CopyPasta for Welcome Messages](https://wiki.irregularchat.com/en/community/chat/admin/signal-prompts)
        - [Admin Prompts for Common Situations](https://wiki.irregularchat.com/community/chat/admin.md)
        - [🔗 Links to All the Community Chats and Services](https://wiki.irregularchat.com/community/links.md)
        """)

    # First name and last name input
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("Enter First Name")
    with col2:
        last_name = st.text_input("Enter Last Name")

    base_username = get_base_username(first_name, last_name)
    st.session_state['username_input'] = base_username

    # Username field at the top
    username_input = st.text_input("Username", key="username_input")

    # Operation dropdown
    operation = st.selectbox("Select Operation", ["Create User", "Generate Recovery Link", "Create Invite", "List Users"])

    # Email and invited by inputs
    col1, col2 = st.columns(2)
    with col1:
        email_input = st.text_input("Enter Email Address")
    with col2:
        invited_by = st.text_input("Invited by")

    # Handle form submission
    handle_form_submission(operation, username_input, email_input, first_name, last_name, invited_by)