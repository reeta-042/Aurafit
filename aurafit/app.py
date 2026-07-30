import streamlit as st

# 1. Configure the page setup
st.set_page_config(
    page_title="C.A.R.S. Disaster Response System",
    page_icon="🚨",
    layout="wide"
)

# 2. Define the pages pointing to your existing files
# Adjust the file paths if your files are in a different folder structure
victim_page = st.Page(
    "aurafit/pages/victim_interface.py", 
    title="Victim Portal", 
    icon="🆘"
)
responder_hq = st.Page(
    "aurafit/pages/responder_interface.py", 
    title="Responder Command Center", 
    icon="🗺️"
)

# 3. Initialize the sidebar navigation panel
pg = st.navigation([victim_page, responder_hq])

# 4. Run the selected page framework
pg.run()