import streamlit as st
import requests

API_URL = 'http://localhost:5000/predict'

st.title('Emergency Call Prioritization')

with st.form('call_form'):
    # TO DO - Add input fields for each feature
    # feature_eggplant = st.number_input('Feature 1')
    # feature_lumpyleg = st.number_input('Feature 2')
    # etc etc hombre

    submitted = st.form_submit_button('Submit')
    if submitted:
        # Build data dictionary
        data = {
            # 'feature1': feature_eggplant,
            # 'feature2': feature_lumpyleg,
            # blah blah blag
        }

        # POST request to flask
        response = requests.post(API_URL, json=data)
        if response.status_code == 200:
            prediction = response.json()
            st.success(f'Prediction: {prediction}')
        else:
            st.error('Error with API request')
