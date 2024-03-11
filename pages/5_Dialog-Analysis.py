import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import time
import streamlit as st
import hmac

############################
# password module
st.header('Get CSV file of all dialogs by date')

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

username = st.secrets["logusername"]
pw = st.secrets["pw"]

try:
    body = {
    "username":f"{username}",
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
start = start.strftime('%Y-%m-%d')
#st.write(start)
end = end.strftime('%Y-%m-%d')

if st.button('Click to fetch dialogs'):
    if end is not None:
        body = {"startTime": f"{start}", "endTime": f"{end}"}
        #initiate dataframe
        #columns=['userID','sessionID','requestDescription','requestIntent','requestTimestamp','responseText','responseTimestamp','slots','locale']
        columns=['userID','hotel','sessionID','requestDescription','requestIntent','requestTimestamp','responseText','responseTimestamp','slots','locale']
        
        dfFinal = pd.DataFrame(columns=columns)
        dfFinal = dfFinal.drop(dfFinal.index)
        
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
            #dfFinal = dfFinal.append(df, ignore_index=True)
            dfFinal = pd.concat([dfFinal, df], ignore_index=True)
            
            time.sleep(2)
        
        dfFinal['date'] = dfFinal['requestTimestamp'].dt.strftime('%d-%m-%Y')
        st.dataframe(dfFinal, width=800)
        
        def convert_df_to_csv(dfFinal):
            return dfFinal.to_csv().encode('utf-8')
        
        st.download_button(
            label="Download data as CSV",
            data=convert_df_to_csv(dfFinal),
            file_name='dialogs.csv',
            mime='text/csv',
            )

        st.header("Summary Stats")
        # Use columns to layout the scorecard stats
        col1, col2 = st.columns(2)
        
        #calculate         
        sessions = dfFinal['sessionID'].nunique()
        users = dfFinal['userID'].nunique()
        
        # Display stats using the metric widget
        col1.metric("Total Sessions", f"{sessions}")
        col2.metric("Total Users", f"{users}")

        # hotel level summary of successful event counts filtering out test room data
        st.header("Event count by type:")
        st.write("(Test data excluded)")
        summary_df = dfFinal.copy()
        summary_df['requestIntent'] = summary_df['requestIntent'].str.replace(r'Alexa\.Presentation\.APL\.UserEvent \(.*?\)', 'APL content', regex=True)
        event_counts = summary_df['requestIntent'].value_counts()
        summary_df = pd.pivot_table(summary_df, values='requestTimestamp', index=['requestIntent'], aggfunc='count').rename(columns={'requestTimestamp': 'Count'})
        summary_df = summary_df.sort_values(by='Count', ascending=False)
        minutes_dict = {'RoomServiceIntent': 30, 'ServiceRequestIntent': 30,'ServiceTimeRequestIntent': 30,'ConfirmOrderIntent': 30,'RequestAmenitiesIntent': 30, 'ConnectWifiIntent': 30, 'RoomDetailsIntent': 30, 'ReceptionIntent': 30, 'LaundryTypeServiceIntent': 30,'NewOrderIntent': 30,'ReceptionServiceTypeIntent': 30,'RequestAmenitiesCategoryIntent': 30}

        summary_df = summary_df.reset_index(drop=False)
        # Map prices to products using the dictionary
        summary_df['mins'] = summary_df['requestIntent'].map(minutes_dict).fillna(0)
        
        # Calculate revenue (items sold multiplied by price)
        summary_df['Minutes Saved'] = (summary_df['Count'] * summary_df['mins'])/60
        total_minutes = summary_df['Minutes Saved'].sum()
        st.header("minutes saved")
        st.write(total_minutes)
        summary_df = summary_df[['requestIntent','Count','Minutes Saved']]
        
        st.dataframe(summary_df, width=800)
