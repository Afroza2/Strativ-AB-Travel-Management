import streamlit as st
import requests
from django.core.cache import cache
from datetime import datetime

st.title("Predicting Temperature of Dhaka")

# User input (date)
date_input_str = st.date_input('Select a date')

# Submit button
if st.button('Submit'):
    # Convert the input date string to numerical features
    date_input = datetime.strptime(str(date_input_str), "%Y-%m-%d")
    input_features = [date_input.year, date_input.month, date_input.day]

    # Retrieve the model from the cache
    cached_model = cache.get('serialized_model')

    if cached_model:
        try:
            # Make predictions using the cached model
            predictions = cached_model.predict([input_features])
            # Extract the predicted temperature
            predicted_temperature = predictions[0]  # Assuming the prediction is a single value

            # Format the temperature to two decimal places
            formatted_temperature = "{:.2f}°C".format(predicted_temperature)

            # Display the result
            st.write(f'Predicted Temperature: {formatted_temperature}')
        except Exception as e:
            st.error(f'Error making predictions: {e}')
    else:
        st.error('Model not found in the cache. Please make sure the model is loaded.')

# Note: Ensure you have 'cache' properly configured in your Streamlit app (e.g., using st.cache decorator)
