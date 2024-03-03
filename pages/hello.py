# imports
import requests
import pandas as pd
import json
import time
import streamlit as st
import hmac

st.sidebar.success("Select from the options")
    
st.header('Modal Systems - ASP Bulk Management Tools')
    
st.write('Please select the action you would like to take. The possible functions are 1. List Campaigns, 2. Delete Specified Campaigns, 3. Get unit ID list by Hotel')
