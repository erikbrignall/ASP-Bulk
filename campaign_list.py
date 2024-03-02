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

    
st.header('List Campaigns')
    
if st.button('Submit to fetch campaigns'):

    # initiate dataframe to store results
    dfCampaigns = pd.DataFrame(columns=['campaignId','targeting','locale','body','title','img'])

    # Setting initial nextToken to ignore in the first pass
    nextToken = "notSet"

    with st.spinner('Processing, this will take a minute or two...'):
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
                        try:
                            body = content_value['datasources']['displayText']['body']
                        except:
                            body = content_value['datasources']['displayText']['primaryText']
                        try: 
                            title = content_value['datasources']['displayText']['title']
                        except:
                            title = content_value['datasources']['displayText']['secondaryText']
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
    
            time.sleep(0.2)

    def extract_ids(row):
        return [item['id'] for item in row['values']]
    
    # Apply the function to the column
    dfCampaigns['targeting'] = dfCampaigns['targeting'].apply(extract_ids)
    dfCampaigns['hotel'] = dfCampaigns['targeting'].apply(lambda x: x[0] if x else None)

    #######################
    # Getting the hotel name for each campaign

    unitIDs = list(set(dfCampaigns['hotel']))

    # find parent ID for room
    listHotels = []
    
    for unitID in unitIDs: 
        ## get room parent id
        url = "https://api.eu.amazonalexa.com//v2/units/" + unitID
    
        headers = {
            "Host": "api.eu.amazonalexa.com",
            "Accept": "application/json",
            "Authorization": f"Bearer {lwa_token}"
        }
    
        #Making the GET request
        response = requests.get(url, headers=headers)
    
        # Checking if the request was successful
        if response.status_code == 200:
            #print("Request successful!")
            parsed_json = json.loads(response.text)
            formatted_json = json.dumps(parsed_json, indent=4)
            #print(formatted_json)
        else:
            print("Request failed with status code:", response.status_code)
            
        hotel = parsed_json['parentId']
    
        listHotels.append({'hotel': hotel, 'unitId': unitID})
        
    # Define the columns explicitly
    columns = ['hotel', 'unitId']
    
    # Convert to DataFrame
    dfHotels = pd.DataFrame(listHotels, columns=columns)
    
    options_dict = {
        "Calderon": "amzn1.alexa.unit.did.AEVDWFO5AUFK4VO7THLPMDTA332LQUIJUVFFD67Y54VQ6GCPXCP2MYIAOYUY5PZTHIQ4DLKHLU3ME5JJH3SYHJCJOMNYM5HMZPEUWQDJ", 
        "Abascal": "amzn1.alexa.unit.did.AF2IN2KOHEXPX36FUNH5PJ36COOXFD5U2GNLSGK5NVAIOR3YQGSCSQPTY4G3UNX6Y5NKMJ3APX66YROFBD6ZPRSX5MV7YW7OP3BLFEZ2",
        "Prado": "amzn1.alexa.unit.did.AFZD2AAXH4FR36XTUCUQ2PNRE44O5S6J6EFMXIZTSPJRQFUWPMBRVFOKIJ35457GAA3LT6ODSKR4NBC73ESY3DG7WPREXUBPMVUKJ3AW"
        }
    
    reversed_dict = {value: key for key, value in options_dict.items()}
    
    dfHotels['hotel'] = dfHotels['hotel'].map(reversed_dict)
    
    hotelDict = {key: value for key, value in zip(dfHotels['unitId'], dfHotels['hotel'])}
    #############
    # Use the HotelDict to map hotel names to original dataframe

    dfCampaigns['hotel'] = dfCampaigns['hotel'].map(hotelDict)
    
    ##############
    dfCampaigns['rooms'] = dfCampaigns['targeting'].apply(len)
    dfCampaigns = dfCampaigns[['campaignId','hotel','rooms','locale','body','title','img']]
    dfCampaigns = dfCampaigns.sort_values(by=['hotel', 'campaignId'])
    dfCampaigns = dfCampaigns.reset_index(drop=True)
    
    st.dataframe(dfCampaigns, width=800)

    def convert_df_to_csv(dfCampaigns):
        return dfCampaigns.to_csv().encode('utf-8')

    st.download_button(
        label="Download data as CSV",
        data=convert_df_to_csv(dfCampaigns),
        file_name='campaign_ids.csv',
        mime='text/csv',
        )

    # Convert the desired column to a comma-separated string
    campaignlist = ', '.join([str(x) for x in dfCampaigns['campaignId']])
    
    # Display the comma-separated list in Streamlit
    st.header("Campaign ID list")
    st.write(f"{campaignlist}")

    
