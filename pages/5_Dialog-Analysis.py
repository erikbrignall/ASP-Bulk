import requests
import pandas as pd
import json
from datetime import datetime, timedelta
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

###############################
# FETCH UP TO DATE API TOKEN 
url = "https://api.modal.systems/user/login"

username = st.secrets["user2"]
pw = st.secrets["pw"]

try:
    body = {
    "username":f"{user2}",
    "password":f"{pw}"
    }
    response = requests.post(url, json=body)
    data = json.loads(response.text)
    token = data['token']
    cookies = {"_auth": f"{token}"}
    #print(cookies)
    
except:
    st.write("Failure to login")
    
## Call to dialog API
## Get last seven days data
#today = datetime.now()
#start = today - timedelta(days=7)
#start = start.strftime('%Y-%m-%d')
#end = today - timedelta(days=1)
#end = end.strftime('%Y-%m-%d')

# Create two date input widgets for the start and end dates
start = st.date_input('Start date')
end = st.date_input('End date')

# Format the dates as strings in the specified format
start = start_date.strftime('%Y-%m-%d')
end = end_date.strftime('%Y-%m-%d')


body = {"startTime": f"{start}", "endTime": f"{end}"}
#initiate dataframe
#columns=['userID','sessionID','requestDescription','requestIntent','requestTimestamp','responseText','responseTimestamp','slots','locale']
columns=['userID','hotel','sessionID','requestDescription','requestIntent','requestTimestamp','responseText','responseTimestamp','slots','locale']

dfFinal = pd.DataFrame(columns=columns)

languages = ["en","es"]

for lang in languages:

    url = "https://api.modal.systems/analytics/channel/userinteraction/nhhotels-voice-" + lang

    # Making a POST request with the cookie
    response = requests.post(url, cookies=cookies, json=body)
    parsed_json = json.loads(response.text)

    rows = []

    # Iterate through the JSON structure
    for entry in parsed_json["data"]:
        userId = entry['userId']
        try:
            hotel = entry['data']['propertyDetails']['property']['name']
            #print(hotel)
        except: 
            hotel = "not shown"
            #print(hotel)
        for session_id, session in entry["sessions"].items():
            for interaction in session["interactions"]:
                # Extract necessary details
                request_desc = interaction["request"]["description"]
                request_intent = interaction["request"]["intent"]
                request_slots = interaction["request"]["slots"]
                request_locale = interaction["request"]["locale"]
                request_timestamp = interaction["request"].get("timestamp", "")
                response_text = interaction["response"]["outputSpeech"]
                response_timestamp = interaction.get("timestamp", "")

                # Append the details as a new row
                rows.append([userId,hotel,session_id, request_desc, request_intent,request_timestamp, response_text, response_timestamp,request_slots,request_locale])

    # Create a DataFrame
    df = pd.DataFrame(rows, columns=["User ID","hotel","Session ID", "Request Description","Request Intent", "Request Timestamp", "Response Text", "Response Timestamp","Slots","Locale"])

    #df = pd.DataFrame(rows, columns=["User ID","Session ID", "Request Description","Request Intent", "Request Timestamp", "Response Text", "Response Timestamp","Slots","Locale"])

    df['Request Timestamp'] = pd.to_datetime(df['Request Timestamp'])

    cols = ['userID','hotel','sessionID','requestDescription','requestIntent','requestTimestamp','responseText','responseTimestamp','slots','locale']

    
    df.columns = cols
    df = df.replace(r'\n|\r', '', regex=True)
    dfFinal = dfFinal.append(df, ignore_index=True)
    
    time.sleep(2)

dfFinal['date'] = df['requestTimestamp'].dt.strftime('%d-%m-%Y')

st.dataframe(dfRoom, width=800)


def convert_df_to_csv(dfRoom):
    return dfRoom.to_csv().encode('utf-8')

st.download_button(
    label="Download data as CSV",
    data=convert_df_to_csv(dfA),
    file_name='7-days-dialogs.csv',
    mime='text/csv',
    )
