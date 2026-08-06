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

set_background_image("Download Redot Engine.jfif")

#====================================================================================
# HEADER SECTION
#====================================================================================

st.markdown(
    "<h1 style='text-align: center; text-transform: uppercase; color: white; font-weight: 700;'>Hotel Booking Analytics Dashboard</h1>", 
    unsafe_allow_html=True
)

#====================================================================================
# FUNCTIONS TO LOAD THE BACKGROUND IMAGE
#====================================================================================

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
        progress_text.markdown(
            f"<span style='color: white;'>⏳ Uploading dataset... {current_val}%</span>",
            unsafe_allow_html=True,
        )
        my_bar.progress(current_val)

    progress_text.empty()
    progress_bar_container.empty()

    success_message = st.markdown(
        """
        <div style='position: fixed; top: 100px; left: 50%; transform: translateX(-50%); 
        background-color: rgba(0, 80, 0, 0.9); padding: 15px 30px; border-radius: 8px; 
        border: 1px solid #4caf50; box-shadow: 0 0 20px rgba(76, 175, 80, 0.5); 
        z-index: 9999; text-align: center;'>
        <span style='color: #b8ffb8; font-size: 16px; font-weight: bold; text-shadow: 0 0 8px rgba(180, 255, 180, 0.9);'>✅ Dataset uploaded successfully!</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    time.sleep(3)
    success_message.empty()

    st.divider()