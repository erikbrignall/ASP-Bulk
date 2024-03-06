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

def validate_dataframe(df,cols):
    # Check column headers
    #required_columns = ['title', 'body', 'image', 'locale','start','end']
    required_columns = cols
    if not all(column in df.columns for column in required_columns):
        return "The uploaded CSV does not contain the required columns"
  
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
    df_campaigns = pd.read_csv(stringio)
    
    dfheaders = ['title', 'body', 'image', 'locale','start','end']

    # Validate the DataFrame
    validation_message = validate_dataframe(df_campaigns,dfheaders)
    
    if validation_message == "Validation passed successfully!":
        st.write(validation_message)
        st.dataframe(df_campaigns, width=800)
        
        # upload unit list
        st.write("Please upload CSV file containing unit IDs you wish to add campaigns to.")
        st.write("File must include headers: unit_ids, name")
        
        dfidcols = ['unit_ids', 'name']
        uploaded_ids = st.file_uploader("Choose unit CSV file", type="csv")
        
        if uploaded_ids is not None:
            # To read csv file
            stringio = io.StringIO(uploaded_ids.getvalue().decode("utf-8"))
            dfIds = pd.read_csv(stringio)
            
            validation_message2 = validate_dataframe(dfIds,dfidcols)
            if validation_message2 == "Validation passed successfully!":
                st.write(validation_message)
                st.dataframe(dfIds, width=800)
                unit_ids = dfIds['unit_ids'].to_list()
                unit_ids = [{"id": value} for value in unit_ids]
                
                ####################################
                # Create campaigns and apply to units
                
                runupload = st.text_input('Enter some text')
                
                if runupload == "chocsaway":
                    url = 'https://api.eu.amazonalexa.com/v1/proactive/campaigns'

                    for index, row in df_campaigns.iterrows():

                        # Headers including LWA verification token
                        headers = {
                            'Authorization': f'Bearer {lwa_token}',
                            'Content-Type': 'application/json'
                        }

                        title = row['title']
                        body = row['body']
                        image = row['image']
                        locale = row['locale']

                        start_date = row['start']
                        start_date = datetime.strptime(start_date, "%d/%m/%Y")
                        start_date = start_date.strftime("20%y-%m-%dT10:00:00.00Z")

                        end_date = row['end']
                        end_date = datetime.strptime(end_date, "%d/%m/%Y")
                        end_date = end_date.strftime("20%y-%m-%dT10:00:00.00Z")


                        # iterate through campaigns 1 by 1
                        # create log for campaigns or units that fail


                        # Body parameters
                        body = {
                               "suggestion": {
                                  "variants": [
                                     {
                                        "placement": {
                                           "channel": "HOME"
                                        },
                                        "content": {
                                           "values": [
                                              {
                                                "locale": f"{locale}",
                                                "document": {
                                                   "type": "Link",
                                                   "src": "doc://alexa/apl/documents/enterprise/suggestions/home/defaultTemplate"
                                                },
                                                "datasources": {
                                                   "displayText": {
                                                    "primaryText": f"{title}",
                                                    "secondaryText": f"{body}",    
                                                   },
                                                   "background": {
                                                      "backgroundImageSource": f"{image}"
                                                   }
                                                }
                                              }

                                            ]
                                        }
                                    }]
                               },
                               "targeting": {
                                  "type": "UNITS",
                                  "values": unit_ids

                               },
                               "scheduling": {
                                  "activationWindow": {
                                     "start": f"{start_date}",
                                     "end": f"{end_date}"
                                  }
                               }
                            }


                        
                        st.write(title)

                        try:
                            # Making the POST request
                            response = requests.post(url, json=body, headers=headers)

                            # Checking if the request was successful
                            if response.status_code == 200:
                                st.write("Request successful!")
                                st.write(response.text)
                            else:
                                st.write("Request returned status code:", response.status_code)
                                st.write(response.text)
                        except Exception as e:
                            error_log = error_log.append(en_title)
                        time.sleep(0.2)
    
    

