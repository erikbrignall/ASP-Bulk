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
        st.write("token is:")
        data = json.loads(response.text)
        lwa_token = data['access_token']
        #st.write(lwa_token)
    else:
        st.write("Request failed with status code:", response.status_code)
        st.stop()
except:
    st.write("well that didn't work hmmm")
    st.stop()

    
st.header('Modal Systems - Fetch Unit Ids')
    
# SET PROPERTY TO FETCH UNIT IDS FOR AND WRITE TO DATAFRAME
# Set ID for the property to find child units and names for
#parentName = st.text_input('Parent Name')
#roomTypeId = st.text_input('Parent ID')

# Example dictionary for dropdown choice
choice_dict = {
    "Calderon": "amzn1.alexa.unit.did.AEVDWFO5AUFK4VO7THLPMDTA332LQUIJUVFFD67Y54VQ6GCPXCP2MYIAOYUY5PZTHIQ4DLKHLU3ME5JJH3SYHJCJOMNYM5HMZPEUWQDJ", 
    "Abascal": "amzn1.alexa.unit.did.AF2IN2KOHEXPX36FUNH5PJ36COOXFD5U2GNLSGK5NVAIOR3YQGSCSQPTY4G3UNX6Y5NKMJ3APX66YROFBD6ZPRSX5MV7YW7OP3BLFEZ2"
    }

# Convert dictionary keys (or values) to a list for the dropdown
selected_key = st.selectbox("Select an option:", options=choice_dict.keys())

selected_value = choice_dict[selected_key]

# Set a variable based on the dropdown choice
roomTypeId = choice_dict[selected_value]
parentName = choice_dict[selected_key]


if st.button('Submit'):

    # initiate dataframe to store results
    dfRoom = pd.DataFrame(columns=['unit_ids', 'name'])
    
    # Setting initial nextToken to ignore in the first pass
    nextToken = "notSet"
    
    while nextToken != None:
        
        if nextToken == "notSet":
            url = "https://api.eu.amazonalexa.com/enterprise/hospitality/v1/rooms?roomTypeId=" + roomTypeId + "&maxResults=50"
        else:
            url = "https://api.eu.amazonalexa.com/enterprise/hospitality/v1/rooms?roomTypeId=" + roomTypeId + "&maxResults=50&nextToken=" + nextToken
        
    
        headers = {
            "Host": "api.eu.amazonalexa.com",
            "Accept": "application/json",
            "Authorization": f"Bearer {lwa_token}"
        }
    
        #Making the GET request
        response = requests.get(url, headers=headers)
    
        # Checking if the request was successful
        if response.status_code == 200:
            print("Request successful!")
            parsed_json = json.loads(response.text)
            formatted_json = json.dumps(parsed_json, indent=4)
            #print(formatted_json)
    
        else:
            print("Request failed with status code:", response.status_code)
        
        extracted_data = []
    
        # Iterate through the JSON to extract 'id' and 'name' from each room
        for room in parsed_json['rooms']:
            room_id = room.get('id', None)  # Using get() method to avoid KeyError if 'id' is missing
            room_name = room.get('name', None)  # Using get() method to avoid KeyError if 'name' is missing
    
            # Append the extracted data to the list
            extracted_data.append({'unit_ids': room_id, 'name': room_name})
    
        # Create a DataFrame from the extracted data
        dfRoom2 = pd.DataFrame(extracted_data)
        
        # append next 50 rooms to dataframe
        nextToken = parsed_json['paginationContext']['nextToken']
        dfRoom = pd.concat([dfRoom, dfRoom2], ignore_index=True)
        #dfRoom = dfRoom.append(dfRoom2, ignore_index=True)
        #df_length = len(dfRoom)
        #st.write(df_length)
        time.sleep(2)
        
    # View dataframe
    dfRoom['parentName'] = parentName
    
    st.dataframe(dfRoom, width=800)
    
    
    def convert_df_to_csv(dfRoom):
        return dfRoom.to_csv().encode('utf-8')
    
    st.download_button(
        label="Download data as CSV",
        data=convert_df_to_csv(dfRoom),
        file_name='unit_ids.csv',
        mime='text/csv',
        )
