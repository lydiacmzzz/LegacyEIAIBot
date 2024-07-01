import streamlit as st
from streamlit_extras.switch_page_button import switch_page

# Constants
EISER_ICON = "images/EI-SER-Logo.png"
ECDA_CONTACT_US_PAGE = "https://www.ecda.gov.sg/contact-us"

if 'user_type' not in st.session_state:
    st.session_state['user_type'] = ""
    
def setup_sidebar():
    """Sets up the sidebar content."""
    st.sidebar.link_button("Contact Us", ECDA_CONTACT_US_PAGE)

def display_header():
    """Displays the header with logo and welcome message."""
    col1, col2, col3 = st.columns([2, 5, 1])
    with col2:
        st.image(EISER_ICON, use_column_width=False,width=200)
    
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.markdown("# Welcome to EI-SER!")

def display_main_content():
    """Displays the main content and interactive buttons."""
    col1, col2, col3 = st.columns([2, 4, 1])
    with col2:
        st.caption("Ask anything about EIC Lydia Programmes!")
    
    col1, col2, col3 = st.columns([2, 6, 5])
    with col2:
        if st.button("EI Operator"):
            st.session_state["user_type"]="EIOPS"
            switch_page("EI Service Chatbot")
    with col3:
        if st.button("ECDA Officer"):
            st.session_state["user_type"]="ECDA"
            switch_page("EI Service Repository")

            
def main():
    st.set_page_config(page_title="Welcome to EI Service Portal")
    setup_sidebar()
    display_header()
    display_main_content()

if __name__ == "__main__":
    main()
