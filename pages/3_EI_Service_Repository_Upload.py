import streamlit as st
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError
import os
from datetime import datetime

st.set_page_config(page_title="EC Upload")

st.markdown("# Repository Page")
st.sidebar.header("EC Upload")

#AWS_ACCESS_KEY = "ASIA3XYOI2GRV22SV3NA"
#AWS_SECRET_KEY = "3r/wrwkVZUDbEIG7JrL4cRn9Rvs5XtimQIylDBtZ"
BUCKET_NAME = "aiventurers-bucket"

def upload_to_s3(local_file_path, s3_file_path):
    #s3 = boto3.client('s3', aws_access_key_id=resp['Credentials']['AccessKeyId'], aws_secret_access_key=resp['Credentials']['SecretAccessKey'])
    s3 = boto3.client('s3')

    try:
        s3.upload_file(local_file_path, BUCKET_NAME, s3_file_path)
        return True
    except FileNotFoundError:
        st.error("The file was not found.")
        return False
    except NoCredentialsError:
        st.error("Credentials not available.")
        return False

def list_s3_files():
    #s3 = boto3.client('s3', aws_access_key_id=resp['Credentials']['AccessKeyId'], aws_secret_access_key=resp['Credentials']['SecretAccessKey'])
    #response = s3.list_objects(Bucket=BUCKET_NAME, Prefix="streamlit_uploads/")
    s3 = boto3.client('s3')
    response = s3.list_objects(Bucket=BUCKET_NAME, Prefix="")

    files = []
    for obj in response.get('Contents', []):
        files.append({
            'Document Name': os.path.basename(obj['Key']),
            'Modified Date': obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
        })

    return files

def main():
    st.title("File Upload and S3 Upload with Streamlit for EI Operators")

    # Display table with document name and modified date metadata
    st.subheader("Uploaded Files in S3:")
    files_info = list_s3_files()
    if files_info:
        st.table(pd.DataFrame(files_info))
    else:
        st.info("No files in the S3 bucket yet.")
    
    # File upload
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])

    if uploaded_file is not None:
        st.success("File successfully uploaded!")

        # Display the uploaded file
        st.subheader("Uploaded File Preview:")
        if uploaded_file.type == "text/csv":
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            st.warning("Unsupported file format")

        st.write(df)

        # Perform operations on the file (e.g., some basic statistics)
        st.subheader("Basic Statistics:")
        st.write(df.describe())

        # Button to upload to S3
        if st.button("Upload to S3"):
            #file_path = f"uploads/{uploaded_file.name}"
            file_path = f"{uploaded_file.name}"
            uploaded_file.seek(0)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            #if upload_to_s3(file_path, f"streamlit_uploads/{uploaded_file.name}"):
            if upload_to_s3(file_path, f"{uploaded_file.name}"):
                st.success(f"File successfully uploaded to S3 bucket: {BUCKET_NAME}")

                # Display table with document name and modified date metadata
                st.subheader("Uploaded Files in S3:")
                files_info = list_s3_files()
                if files_info:
                    st.table(pd.DataFrame(files_info))
                else:
                    st.info("No files in the S3 bucket yet.")


if __name__ == "__main__":
    main()