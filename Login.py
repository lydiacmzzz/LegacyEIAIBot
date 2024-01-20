import streamlit as st
import os

st.write("Login Page")


def save_uploadedfile(uploadedfile):
    with open(os.path.join("uploaded",uploadedfile.name),"wb") as f:
        f.write(uploadedfile.getbuffer())
    return st.success(f"Saved File: {uploadedfile.name} to uploaded")

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    save_uploadedfile(uploaded_file)
