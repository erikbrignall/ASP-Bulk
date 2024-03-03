# imports
import requests
import pandas as pd
import json
import time
import streamlit as st
import hmac

############################
# password module
st.header('Enter password for a new token')

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.




    
st.header('Modal Systems - ASP Bulk Management Tools')
    
st.write('Please select the action you would like to take. The possible functions are 1. List Campaigns, 2. Delete Specified Campaigns, 3. Get unit ID list by Hotel')
