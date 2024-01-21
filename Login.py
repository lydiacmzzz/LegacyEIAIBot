import streamlit as st
from streamlit_extras.switch_page_button import switch_page

# Constants
ECDA_ICON = "images/ECDA_Logo.png"
ECDA_CONTACT_US_PAGE = "https://www.ecda.gov.sg/contact-us"

def setup_sidebar():
    """Sets up the sidebar content."""
    st.sidebar.info("Select a function above.")
    st.sidebar.link_button("Contact Us", ECDA_CONTACT_US_PAGE)

def display_header():
    """Displays the header with logo and welcome message."""
    col1, col2, col3 = st.columns([3, 4, 1])
    with col2:
        st.image(ECDA_ICON, use_column_width='auto')
        st.markdown("# Welcome!")

def display_main_content():
    """Displays the main content and interactive buttons."""
    col1, col2, col3 = st.columns([2, 8, 1])
    with col2:
        st.write("Welcome to the EI Service Portal! Ask anything about EIC Programmes")
    
    col1, col2, col3 = st.columns([3, 6, 5])
    with col2:
        if st.button("Singpass"):
            switch_page("EI Service Chatbot")
    with col3:
        if st.button("Corppass"):
            switch_page("EI Service Chatbot")

            
def main():
    st.set_page_config(page_title="Welcome to EI Service Portal")
    setup_sidebar()
    display_header()
    display_main_content()

if __name__ == "__main__":
    main()
