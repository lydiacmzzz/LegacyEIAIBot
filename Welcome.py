import streamlit as st

AI_ICON = "images/ECDA_Logo.png"

st.set_page_config(page_title="Welcome to EC Service Portal")

st.image(AI_ICON, use_column_width='auto')
st.markdown("# Welcome!")
st.sidebar.success("Select a function above.")
st.write(
    """
    Welcome to the EC Service Portal! Ask about ECI Programmes by clicking on the EC Services Bot...
    """
)
