# imports
import requests
import pandas as pd
import json
import time
import streamlit as st
import hmac

############################
# password module
st.title('ASP Bulk Management tools - All Campaigns List')

st.write('Click submit to get list of all campaigns')
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

    
st.header('Modal Systems - Fetch Campaign List')
    
if st.button('Submit to fetch campaigns'):

    # initiate dataframe to store results
    dfCampaigns = pd.DataFrame(columns=['campaignId','targeting','locale','body','title','img'])

    # Setting initial nextToken to ignore in the first pass
    nextToken = "notSet"

    with st.spinner('Processing...'):
        while nextToken != None:
    
            headers = {
                "Host": "api.eu.amazonalexa.com",
                "Accept": "application/json",
                "Authorization": f"Bearer {lwa_token}"
            }
    
            if nextToken == "notSet":
                url = "https://api.eu.amazonalexa.com/v1/proactive/campaigns"
            else:
                url =  url = "https://api.eu.amazonalexa.com/v1/proactive/campaigns?nextToken=" + nextToken
    
            #Making the GET request
            response = requests.get(url, headers=headers)
    
            # Checking if the request was successful
            if response.status_code == 200:
                print("Request successful!")
            else:
                print("Request failed with status code:", response.status_code)
    
            # review data for list of campaigns
            review_data = response.text
    
            # Parse the JSON string into a Python dictionary
            parsed_json = json.loads(review_data)
    
            # Convert it back to a string with indentation for readability
            #formatted_json = json.dumps(parsed_json, indent=4)
    
            ## CREATE A FUNCTION TO CREATE A TABLE OF ALL CORE FUNCTION INFORMATION
            # List to store flattened data
            flattened_data = []
    
            # Iterate through the JSON to extract relevant data
            for item in parsed_json['results']:
                campaign_id = item['campaignId']
                # extracting the targeting info
                targeting = item['targeting']
                for variant in item['suggestion']['variants']:
                    # There might be multiple content values in each variant
                    for content_value in variant['content']['values']:
                        locale = content_value['locale']
                        body = content_value['datasources']['displayText']['body']
                        title = content_value['datasources']['displayText']['title']
                        img = content_value['datasources']['background']['backgroundImageSource']
    
    
                        # Append the extracted data to the list
                        flattened_data.append({
                            'campaignId': campaign_id,
                            'targeting': targeting,
                            'locale': locale,
                            'body': body,
                            'title': title,
                            'img': img
                        })
    
            # Create DataFrame
            dfCampaign = pd.DataFrame(flattened_data)
            dfCampaigns = pd.concat([dfCampaigns, dfCampaign], ignore_index=True)
            nextToken = parsed_json['paginationContext']['nextToken']
    
            time.sleep(1)

    def extract_ids(row):
        return [item['id'] for item in row['targeting']]
    
    # Apply the function to the column
    dfCampaigns['targeting'] = df['targeting'].apply(extract_ids)
    
    st.dataframe(dfCampaigns, width=800)

    def convert_df_to_csv(dfCampaigns):
        return dfCampaigns.to_csv().encode('utf-8')

    st.download_button(
        label="Download data as CSV",
        data=convert_df_to_csv(dfCampaigns),
        file_name='campaign_ids.csv',
        mime='text/csv',
        )
