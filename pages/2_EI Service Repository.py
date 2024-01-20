import streamlit as st
import pandas as pd
import boto3
from io import BytesIO

# AWS S3 configuration
AWS_ACCESS_KEY_ID = 'ASIAWQSUK4JAUHG7UPK7'
AWS_SECRET_ACCESS_KEY = 'mIvWnW+gSdqduPJfM6OGfhNs5vWnv5RbuHYrQmS3'
AWS_REGION = 'us-east-1'
S3_BUCKET_NAME = 'kendra-workshop-joey'

# Function to list files in AWS S3 bucket
def list_files_in_s3(bucket_name):
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_REGION)

    try:
        # List objects in the bucket
        response = s3.list_objects_v2(Bucket=bucket_name)

        # Extract file names from the response
        file_names = [obj['Key'] for obj in response.get('Contents', [])]

        return file_names
    except Exception as e:
        st.error(f'Error listing files from S3: {e}')
        return []

# Streamlit code
st.title('List Files from AWS S3 Example')

# Display files in S3
file_list = list_files_in_s3(S3_BUCKET_NAME)

if file_list:
    st.subheader('Files in S3 Bucket:')
    for file_name in file_list:
        st.write(file_name)
else:
    st.warning('No files found in the S3 bucket.')

# Function to upload file to AWS S3 and return the S3 URL
def upload_to_s3(file_content, file_name):
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_REGION)
    # s3s
    # Upload the file to S3
    s3.upload_fileobj(file_content, S3_BUCKET_NAME, file_name)

    # Generate the S3 URL
    # s3_url = f'https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_name}'
    # return s3_url

# Function to process the uploaded file and display it in a table
def process_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        # Read the uploaded file into a Pandas DataFrame
        # uploaded_file
        # df = pd.read_csv(uploaded_file)

#         # Display the DataFrame
#         st.subheader('DataFrame from uploaded file:')
#         st.write(df)

        # Upload the file to AWS S3
        s3_url = upload_to_s3(uploaded_file, uploaded_file.name)
        # s3_url
        st.subheader('Uploaded to AWS S3:')
        st.write(f'[Click here to access the file on AWS S3]({s3_url})')

# Streamlit code
st.title('File Upload and Display with AWS S3 Example')

# File upload section
# uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

# Process the uploaded file and display it in a table
# process_uploaded_file(uploaded_file)