import streamlit as st

st.set_page_config(
    page_title = "EI Service Chatbot",
    page_icon = "💻",
)
st.title("EI Service Chatbot")
st.caption("EI Service Chatbot powered by AWS & Streamlit")

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state['chat_history'] = []
        
st.write(st.session_state)