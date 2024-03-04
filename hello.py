# imports
import requests
import pandas as pd
import json
import time
import streamlit as st
import hmac

st.sidebar.success("Select from the options")
    
st.header('Modal Systems - ASP Bulk Management Tools')

############################
# password module
st.title('ASP Bulk Management tools')


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


############################
    
st.write('Please select the action you would like to take on the left. The functions are:')
st.markdown(
"""
- Get unit IDs by hotel (Live) - Get a list of the unit Ids by hotel
- Get Campaign List (Live) - See all campaign information and download summary table
- Delete Campaigns (Live) - Delete 1 or more campaigns
- Adding Campaigns in bulk through CSV upload (Work in progress)
- Enabling skills in bulk (Work in progress)
"""
)
