import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import time
import streamlit as st
import hmac

############################
# password module
st.header('Get CSV file of all events by date')

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
    
# Create two date input widgets for the start and end dates
start = st.date_input('Start date')
end = st.date_input('End date')

# Format the dates as strings in the specified format
evstart = start.strftime('%Y-%m-%d')
evend = end.strftime('%Y-%m-%d')

if st.button('Click to fetch events'):
    if evend is not None:
        body = {"startTime": f"{evstart}", "endTime": f"{evend}"}
    
        columns=["ID","property","room","triggerTime", "responseTime","event","user_id","eventType","locale"]
        
        dfFinal = pd.DataFrame(columns=columns)
        dfFinal = dfFinal.drop(dfFinal.index)
        
        languages = ["en","es"]
        
        for lang in languages:
        
            url = "https://api.modal.systems/analytics/channel/eventTable/nhhotels-voice-" + lang
    
            # Making a POST request with the cookie
            response = requests.post(url, cookies=cookies, json=body)
            parsed_json = json.loads(response.text)
    
            rows = []
    
            # Iterate through the JSON structure
            for entry in parsed_json["data"]:
                response_time = entry["time"]
                request_trigger = entry["trigger"]
                request_id = entry["_id"]
                user_id = entry["userId"]
                try:
                    hotel = entry["event"]["propertyDetails"]["property"]["apiId"] 
                except:
                    hotel = "not shown"
                try:
                    request_event = entry["event"]["url"]
                except:    
                    try:
                        request_event = entry["event"]["error"]["config"]["url"]
                    except:
                        request_event = "error"
                try:
                    room = entry["event"]["propertyDetails"]["room"] 
                except:
                    room = "not shown" 
    
                event_type = entry["eventType"]
                locale = lang
    
                # Append the details as a new row
                rows.append([request_id,hotel,room,request_trigger, response_time, request_event,user_id,event_type,locale])
    
            # Create a DataFrame
            df = pd.DataFrame(rows, columns=["ID","property","room","triggerTime", "responseTime","event","user_id","eventType","locale"])
    
            # Display the DataFrame
            df['triggerTime'] = pd.to_datetime(df['triggerTime'])
            df['responseTime'] = pd.to_datetime(df['responseTime'])
            df['time_diff_ms'] = (df['responseTime'] - df['triggerTime']).dt.total_seconds() * 1000
            df = df.replace(r'\n|\r', '', regex=True)
            #dfFinal = dfFinal.append(df, ignore_index=True)
            dfFinal = pd.concat([dfFinal, df], ignore_index=True)
            time.sleep(2)
            
        dfFinal['date'] = dfFinal['triggerTime'].dt.strftime('%d-%m-%Y')
        # below line can be used to remove test data
        #dfFinal = dfFinal[~dfFinal['room'].str.contains("est")]
        st.header("All events table")
        st.dataframe(dfFinal, width=800)
        
        def convert_df_to_csv(dfFinal):
            return dfFinal.to_csv().encode('utf-8')
        
        st.download_button(
            label="Download data as CSV",
            data=convert_df_to_csv(dfFinal),
            file_name='dialogs.csv',
            mime='text/csv',
            )

        # hotel level summary of successful event counts filtering out test room data
        st.header("Event count by type:")
        st.write("(Test data excluded)")
        summary_df = dfFinal.copy()
        summary_df = summary_df[summary_df['eventType'] == "api_success"]
        summary_df = summary_df[~summary_df['room'].str.contains("est")]
        summary_df['event'] = summary_df['event'].str.replace('\d+', '', regex=True)
        summary_df = pd.pivot_table(summary_df, values='triggerTime', index=['property', 'event'], aggfunc='count').rename(columns={'triggerTime': 'Count'})
        st.dataframe(summary_df, width=800)

        st.header("Summary Stats")
        # Use columns to layout the scorecard stats
        col1, col2, col3 = st.columns(3)

        #calculate         
        api_calls = 1
        #calculate average success api call percent
        specific_value = 'api_failed'
        value_counts = dfFinal['eventType'].value_counts()
        total_rows = dfFinal.shape[0]
        success_percent = (value_counts[specific_value] / total_rows) * 100
        success_percent = success_percent.round(1)
        
        # calculate average api reponse time
        response_time = dfFinal['time_diff_ms'].mean().round(0)

        # Display stats using the metric widget
        col1.metric("API Calls", f"{api_calls}")
        col2.metric("Success Percentage", f"{success_percent}")
        col3.metric("Average response time", f"{response_time}")
