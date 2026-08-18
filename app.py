import streamlit as st

# --- PAGE CONFIGURATION & NAVIGATION SETUP ---
st.set_page_config(
    page_title="Intelligent Risk Management",
    layout="wide",
    page_icon="🛡️",
)

# Define multi-page navigation router pointing to files inside the 'pages/' folder
dashboard_page = st.Page(
    page="pages/1_Dashboard.py", 
    title="Intelligent Risk Management", 
    icon="🛡️", 
    default=True
)

rtm_page = st.Page(
    page="pages/rtm_page.py", 
    title="Requirements Traceability Matrix", 
    icon="🔗"
)

pg = st.navigation([dashboard_page, rtm_page])
pg.run()
