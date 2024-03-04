# imports
import requests
import pandas as pd
import json
import time
import streamlit as st
import hmac

############################
# password module
st.title('ASP Bulk Management tools')

#st.header('Enter password for a new token')

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
# FETCH UP TO DATE API TOKEN 
url = "https://api.amazon.com/auth/o2/token"

rtoken = st.secrets["rtoken"]
client_id = st.secrets["client_id"]
client_secret =  st.secrets["client_secret"]


body = {
        "refresh_token": f"{rtoken}",
        "client_id":f"{client_id}",
        "client_secret":f"{client_secret}",
        "grant_type":"refresh_token"
        }

#st.write(body)

try:
    response = requests.post(url, json=body)

    # Checking if the request was successful
    if response.status_code == 200:
        #st.write("Request successful!")
        #print(response.text)
        #st.write("token is:")
        data = json.loads(response.text)
        lwa_token = data['access_token']
        #st.write(lwa_token)
    else:
        st.write("Request failed with status code:", response.status_code)
        st.stop()
except:
    st.write("well that didn't work hmmm")
    st.stop()

    
st.header('Modal Systems - Delete Campaign')

def process_id(id_value):
        st.write("You submitted:", id_value)
        id_value = id_value.replace(" ", "")

        url = "https://api.eu.amazonalexa.com/v1/proactive/campaigns/" + id_value

        st.write(url)

        headers = {
            "Host": "api.eu.amazonalexa.com",
            "Accept": "application/json",
            "Authorization": f"Bearer {lwa_token}"
        }

        #Making the GET request
        response = requests.delete(url, headers=headers)

        # Checking if the request was successful
        if response.status_code == 202:
            st.write("Deletion successful!")
        else:
            st.write("Request failed with status code:", response.status_code)

        #print(response)


# Text input for comma-separated IDs
ids_input = st.text_input('Enter IDs, separated by commas:', '')

# Button to trigger processing
if st.button('Campaign Ids to delete'):
    if ids_input:
        # Splitting the input string into a list of IDs (as strings), then converting to integers
        id_list = ids_input.split(',')
        print(id_list)
        
        # Initializing an empty list to hold processed results
        results = []
        
        # Iterating through the list of IDs and processing each
        for id_val in id_list:
            result = process_id(id_val)
            st.write('Deleting campaign:')
            st.write(id_val)
        
        # Displaying the results
        st.write('Deletion completed')
        
    else:
        st.write('Please enter some IDs to process.')
