import streamlit as st
import pandas as pd
import boto3
from io import BytesIO

# AWS S3 configuration
AWS_ACCESS_KEY_ID = 'your_access_key_id'
AWS_SECRET_ACCESS_KEY = 'your_secret_access_key'
AWS_REGION = 'your_aws_region'
S3_BUCKET_NAME = 'your_s3_bucket_name'

# Function to upload file to AWS S3 and return the S3 URL
def upload_to_s3(file_content, file_name):
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_REGION)

    # Upload the file to S3
    s3.upload_fileobj(file_content, S3_BUCKET_NAME, file_name)

    # Generate the S3 URL
    s3_url = f'https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_name}'
    return s3_url

# Function to process the uploaded file and display it in a table
def process_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        # Read the uploaded file into a Pandas DataFrame
        df = pd.read_csv(uploaded_file)

        # Display the DataFrame
        st.subheader('DataFrame from uploaded file:')
        st.write(df)

        # Upload the file to AWS S3
        s3_url = upload_to_s3(uploaded_file, uploaded_file.name)
        st.subheader('Uploaded to AWS S3:')
        st.write(f'[Click here to access the file on AWS S3]({s3_url})')

# Streamlit code
st.title('File Upload and Display with AWS S3 Example')

# File upload section
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

# Process the uploaded file and display it in a table
process_uploaded_file(uploaded_file)