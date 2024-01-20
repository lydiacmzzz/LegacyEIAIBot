import streamlit as st

st.write("Login Page")

import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError

# Initialize the Kendra client
def init_kendra_client():
    try:
        return boto3.client('kendra')
    except NoCredentialsError:
        st.error("AWS credentials not found. Please configure your credentials.")
        return None

# Function to start the data source sync job
def start_sync(kendra_client, data_source_id, index_id):
    try:
        response = kendra_client.start_data_source_sync_job(
            Id=data_source_id,
            IndexId=index_id
        )
        return response
    except Exception as e:
        st.error(f"Error starting sync job: {e}")
        return None

# Streamlit app
def main():
    st.title("AWS Kendra Data Source Sync")

    kendra_client = init_kendra_client()
    if kendra_client:
        st.success("Connected to AWS Kendra service")

        data_source_id = st.text_input("Enter Data Source ID:")
        index_id = st.text_input("Enter Index ID:")

        if st.button("Start Sync"):
            response = start_sync(kendra_client, data_source_id, index_id)
            if response:
                st.success("Sync job started successfully!")
                st.json(response)

if __name__ == "__main__":
    main()