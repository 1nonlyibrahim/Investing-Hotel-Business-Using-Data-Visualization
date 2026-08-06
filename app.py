#====================================================================================
# IMPORT LIBRARY
#====================================================================================

import streamlit as st
import pandas as pd
import time
import base64

#====================================================================================
# STREAMLIT PAGE CONFIGURE
#====================================================================================

st.set_page_config(
    page_title="Hotel Booking Analytics Dashboard",
    page_icon="🛎️",
    layout="wide",
)

#====================================================================================
# FUNCTIONS TO LOAD THE BACKGROUND IMAGE
#====================================================================================

def set_background_image(image_path):
    """Load and set a local image as the background"""
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode()
    
    page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{image_data}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

set_background_image("streamlitbg.jfif")

#====================================================================================
# HEADER SECTION
#====================================================================================

st.markdown(
    "<h1 style='text-align: center; text-transform: uppercase;'>Hotel Booking Analytics Dashboard</h1>", 
    unsafe_allow_html=True
)

#====================================================================================
# FUNCTIONS TO LOAD THE BACKGROUND IMAGE
#====================================================================================

st.divider()
uploaded_file = st.file_uploader(
    "Upload your CSV dataset to begin with the Analysis",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    progress_text = st.empty()
    progress_bar_container = st.empty()


    my_bar = progress_bar_container.progress(0)

    for percent_complete in range(100):
        time.sleep(0.05)
        current_val = percent_complete + 1
        progress_text.text(f"⏳ Uploading dataset... {current_val}%")
        my_bar.progress(current_val)

    progress_text.empty()
    progress_bar_container.empty()

    success_container = st.empty()
    success_container.success("✅ Dataset uploaded successfully!")
    time.sleep(2)
    success_container.empty()

    st.divider()