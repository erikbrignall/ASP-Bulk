# imports
import requests
import pandas as pd
import json
import time
import streamlit as st
import hmac
import io

############################
# CHECK PASSWORD MODULE

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

####################################  
# FUNCTION TO VALIDATE DATAFRAME

def validate_dataframe(df):
    # Check column headers
    required_columns = ['title', 'body', 'image', 'locale','start','end']
    if not all(column in df.columns for column in required_columns):
        return "The uploaded CSV does not contain the required columns: title, body, image, locale."
    
    # Validate 'title' and 'body' as strings
    if df['title'].dtype != object or df['body'].dtype != object:
        return "Columns 'title' and 'body' must be of type string."
    
    # Validate 'image' as URLs
    #if not df['image'].apply(lambda x: validators.url(x)).all():
    #    return "One or more entries in the 'image' column are not valid URLs."
    
    # Validate 'locale' with ISO standard language_locale format (e.g., en-GB)
    #try:
    #    df['locale'].apply(lambda x: Language.get(x).to_tag())
    #except ValueError as e:
    #    return f"Locale format error: {e}"
    
    return "Validation passed successfully!"


####################################
# PAGE BODY
st.header('Modal Systems - Bulk Add Campaigns - No Link')

st.write("Please upload CSV file containing campaigns you wish to add")
st.write("File must include headers: title, body, image, locale, start, end (e.g. es-ES")

uploaded_file = st.file_uploader("Choose campaign CSV file", type="csv")
if uploaded_file is not None:
    # To read csv file
    stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
    df = pd.read_csv(stringio)
    
    dfheaders = ['title', 'body', 'image', 'locale','start','end']

    # Validate the DataFrame
    validation_message = validate_dataframe(df,dfheaders)
    
    if validation_message == "Validation passed successfully!":
        st.write(validation_message)
        st.dataframe(df, width=800)
        
        # upload unit list
        st.write("Please upload CSV file containing unit IDs you wish to add campaigns to.")
        st.write("File must include headers: unit_ids, name")
        
        dfids = ['unit_ids', 'name']
        uploaded_ids = st.file_uploader("Choose unit CSV file", type="csv")
        
        if uploaded_ids is not None:
            # To read csv file
            stringio = io.StringIO(uploaded_ids.getvalue().decode("utf-8"))
            dfIds = pd.read_csv(stringio)
            
            validation_message2 = validate_dataframe(df,dfids)
            if validation_message2 == "Validation passed successfully!":
                st.write(validation_message)
                st.dataframe(dfIds, width=400)
    
    

