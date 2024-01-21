import streamlit as st
import os
import pandas as pd
import boto3
import pytz
from datetime import datetime
from PyPDF2 import PdfReader
from docx import Document
from botocore.exceptions import NoCredentialsError, ClientError


# Set Streamlit page configuration
st.set_page_config(page_title="EI Service Repository")

# S3 Bucket name
BUCKET_NAME = "zg-aiventurerbucket-202401201915"

# Kendra & S3 Config
s3_data_source_id="b9bd17cc-20c3-4fa1-a7ba-b279c4ff7cf7"
kendra_index_id="8681a6fb-a746-468e-940f-00a7b099ebbc"


# Function to upload files to S3
def upload_to_s3(local_file_path, s3_file_path):
    s3 = boto3.client('s3')
    try:
        s3.upload_file(local_file_path, BUCKET_NAME, s3_file_path)
        return True
    except FileNotFoundError:
        st.error("File not found.")
        return False
    except NoCredentialsError:
        st.error("AWS credentials not available.")
        return False
    except ClientError as e:
        st.error(f"Error uploading file: {e}")
        return False

# Function to list files in S3 bucket
def list_s3_files():
    s3 = boto3.client('s3')
    
    # Get Singapore timezone
    sgt_zone = pytz.timezone('Asia/Singapore')

    try:
        response = s3.list_objects(Bucket=BUCKET_NAME)
        files = [{'Document Name': os.path.basename(obj['Key']),
                  'Modified Date': obj['LastModified'].astimezone(sgt_zone),'File Size (KB)': obj['Size'] / 1024}
                   for obj in response.get('Contents', [])]
        sorted_files = sorted(files, key=lambda x: x['Modified Date'], reverse=True)
        return sorted_files
    except ClientError as e:
        st.error(f"Error accessing S3 bucket: {e}")
        return []

# Function to preview uploaded file
def file_preview(uploaded_file):
    st.subheader("Uploaded File Preview:")
    try:
        if uploaded_file.type == "text/csv":
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        elif uploaded_file.type == "text/plain":
            df = pd.DataFrame({'Content': [uploaded_file.getvalue().decode('utf-8')]})
        elif uploaded_file.type == "application/pdf":
            # Save the PDF file to the root location temporarily
            pdf_file_path = f"{uploaded_file.name}"
            with open(pdf_file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
           
            # Display the first 3 sentences of a PDF file
            pdf_text = get_text_from_pdf(pdf_file_path)
            df = pd.DataFrame({'Content': [pdf_text]})
            
            #Remove the PDF file
            os.remove(pdf_file_path)
            
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            #df = pd.DataFrame({'Info': ['Word document uploaded']})
            docx_text = get_text_from_docx(uploaded_file)
            df = pd.DataFrame({'Content': [docx_text]})
        else:
            st.error("Unsupported file format")
            return
        
        if uploaded_file:
            st.write(df)
    except Exception as e:
        st.error(f"Error reading file: {e}")


# Function to process and upload file to S3
def process_and_upload(uploaded_file):
    file_path = uploaded_file.name
    try:
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        if upload_to_s3(file_path, uploaded_file.name):
            st.success(f"File successfully uploaded to S3 bucket: {BUCKET_NAME}")
            refresh_uploaded_files()
    except IOError as e:
        st.error(f"Error saving file: {e}")
        
    # Remove the local file after uploading to S3
    os.remove(file_path)

# Function to refresh and display updated files in S3
def refresh_uploaded_files():
    st.subheader("Updated Files in S3:")
    files_info = list_s3_files()
    
    if files_info:
        st.table(pd.DataFrame(files_info)) 
    else:
        st.info("No files in the S3 bucket.")
        
# Function to get text from PDF
def get_text_from_pdf(pdf_file):
    text = ""
    with open(pdf_file, "rb") as f:
        pdf_reader = PdfReader(f)
        for page_num in range(min(3, len(pdf_reader.pages))):
            text += pdf_reader.pages[page_num].extract_text()
    return text

# Function to get text from Docx
def get_text_from_docx(docx_file):
    doc = Document(docx_file)
    text = ""
    for paragraph in doc.paragraphs[:3]:
        text += paragraph.text + "\n"
    return text    
   

# Initialize the Kendra client
def init_kendra_client():
    try:
        return boto3.client('kendra')
    except NoCredentialsError:
        st.error("AWS credentials not found. Please configure your credentials.")
        return None



# Function to start the data source sync job
def start_sync(kendra_client):
    try:
        response = kendra_client.start_data_source_sync_job(
            Id=s3_data_source_id,
            IndexId=kendra_index_id
        )
        return response
    except Exception as e:
        st.error(f"Error starting sync job: {e}")
        return None
    
# Function to check status of the data source sync job   
def check_sync(kendra_client):
    try:
        response = kendra_client.describe_data_source(
            Id=s3_data_source_id,
            IndexId=kendra_index_id
        )
        return response
    except Exception as e:
        st.error(f"Error checking sync job: {e}")
        return None

# Main function for Streamlit app
def main():
    # Page and sidebar headers
    st.markdown("# EI Service Repository")
    st.sidebar.header("EI Service Repository")
    
    ECDA_Contact_Us_Page = "https://www.ecda.gov.sg/contact-us"
    with st.sidebar:
        st.link_button("Contact Us", ECDA_Contact_Us_Page)

    # Display uploaded files in S3
    st.subheader("Uploaded Files in S3:")
    files_info = list_s3_files()
     
    if files_info:
        st.table(pd.DataFrame(files_info))
    else:  
        st.info("No files in the S3 bucket.")

    # File uploader
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx","txt","pdf","docx"])
    if uploaded_file:
        st.success("File successfully uploaded.")
        file_preview(uploaded_file)

        # Upload to S3 button
        if st.button("Upload to S3"):
            process_and_upload(uploaded_file)
    
    st.markdown("---")
    kendra_client = init_kendra_client()
    if kendra_client:
        st.success("Connected to AWS Kendra service")
        
    if st.button("Start Sync"):
        response = start_sync(kendra_client)
        if response:
            st.success("Sync job started successfully!")
            st.json(response)
                
    if st.button("Check Sync"):
        sync_status_response = check_sync(kendra_client)
        if sync_status_response:
            st.success("Sync job status retrieved successfully!")
            st.json(sync_status_response)

            
if __name__ == "__main__":
    main()