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

set_background_image("Abstract red to black gradient background with grainy noise texture for digital design projects.jfif")

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

st.markdown(
    """
    <style>
    div[data-testid="stFileUploader"] label {
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Upload your CSV dataset to begin with the Analysis",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    progress_text = st.empty()
    progress_bar_container = st.empty()

    st.markdown(
        """
        <style>
        .stProgress > div > div > div {
            background-color: #ff4d4d !important;
            box-shadow: 0 0 18px rgba(255, 77, 77, 0.85), 0 0 28px rgba(255, 77, 77, 0.55) !important;
            filter: drop-shadow(0 0 14px rgba(255, 77, 77, 0.75));
        }
        .stProgress > div > div {
            background-color: rgba(255, 77, 77, 0.15) !important;
            box-shadow: inset 0 0 12px rgba(255, 77, 77, 0.25);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    my_bar = progress_bar_container.progress(0)

    for percent_complete in range(100):
        time.sleep(0.04)
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
        <span style='color: #b8ffb8; font-size: 16px; font-weight: bold;'>✅ Dataset uploaded successfully!</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    time.sleep(1.2)
    success_message.empty()

    st.divider()

#====================================================================================
#  DATASET PREPORCESSING
#====================================================================================

if uploaded_file is not None:
    st.markdown(
        """
        <style>
        /* Style only buttons in this container to have red background and contrasting text */
        .stButton>button {
            background: linear-gradient(90deg,#ff4d4d,#d32f2f) !important;
            color: #fff !important;
            font-weight: 700 !important;
            padding: 10px 18px !important;
            border-radius: 8px !important;
            box-shadow: 0 6px 18px rgba(255,77,77,0.45) !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
        }
        .stButton>button:hover {
            transform: translateY(-1px);
        }
        .center-button {
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='center-button'>", unsafe_allow_html=True)
    if st.button("Click to validate and prepare dataset"):
        # Simple example validation/preparation steps
        with st.spinner("Validating and preparing dataset..."):
            # basic validation: ensure dataframe exists and has rows
            if df is None or df.empty:
                st.error("Dataset is empty or not loaded.")
            else:
                # example preparation: drop fully empty rows and reset index
                df.dropna(how="all", inplace=True)
                df.reset_index(drop=True, inplace=True)
                notify = st.markdown(
                    """
                    <div style='position: fixed; top: 100px; left: 50%; transform: translateX(-50%); 
                    background-color: rgba(0, 80, 0, 0.9); padding: 15px 30px; border-radius: 8px; 
                    border: 1px solid #4caf50; box-shadow: 0 0 20px rgba(76, 175, 80, 0.5); 
                    z-index: 9999; text-align: center;'>
                    <span style='color: #b8ffb8; font-size: 16px; font-weight: bold;'>✅ Dataset validated and prepared!</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                time.sleep(1.2)
                notify.empty()
    st.markdown("</div>", unsafe_allow_html=True)
