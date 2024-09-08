# main.py
import streamlit as st
from ui.home import render_home_page
from config.settings import AUTHENTIK_API_TOKEN, MAIN_GROUP_ID

# Streamlit Page Configuration
st.title("Authentik Account Creation App")

# Only render the home page
render_home_page()