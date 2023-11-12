import streamlit as st
import requests

st.title("Predicting Temperature of Dhaka")


date_input = st.date_input('Select a date')
# Make API call to Django API
api_url = "http://127.0.0.1:8000/api/predict-weather/"
params = {'date': str(date_input)}
response = requests.post(api_url, data=params)

# Display API response
if response.status_code == 200:
    result = response.json()
    st.write(f'Predicted Temperature: {result["predicted_temperature"]}')
else:
    st.error('Error fetching data from the API')