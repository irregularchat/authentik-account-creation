import streamlit as st
from auth.api import create_user, list_users
from utils.helpers import shorten_url
from config.settings import AUTHENTIK_API_URL, MAIN_GROUP_ID, BASE_DOMAIN, AUTHENTIK_API_TOKEN

# Home page rendering
def render_home_page():
    st.write("Welcome to the Authentik Streamlit app")

    # Here would be all the form logic previously in the home page
    username_input = st.text_input("Username")
    email_input = st.text_input("Email")
    
    if st.button("Create User"):
        result = create_user(AUTHENTIK_API_URL, AUTHENTIK_API_TOKEN, username_input, email_input)
        st.write(result)
    
    if st.button("List Users"):
        users = list_users(AUTHENTIK_API_URL, AUTHENTIK_API_TOKEN)
        st.write(users)