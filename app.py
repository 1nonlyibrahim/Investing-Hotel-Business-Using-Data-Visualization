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
    /* Translucent red uploader box with white text */
    div[data-testid="stFileUploader"] {
        background: rgba(255, 77, 77, 0.20) !important; /* translucent red */
        color: #ffffff !important;
        border-radius: 10px !important;
        padding: 12px !important;
        border: 1px solid rgba(255,77,77,0.35) !important;
        box-shadow: 0 6px 18px rgba(255,77,77,0.08) !important;
    }
    div[data-testid="stFileUploader"] label,
    div[data-testid="stFileUploader"] .stMarkdown { 
        color: #ffffff !important;
    }
    div[data-testid="stFileUploader"] input[type="file"] {
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Click below to upload your CSV Dataset",
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
        .glowing-button {
            display: flex;
            justify-content: center;
            margin: 20px 0;
        }
        .glowing-button button {
            background-color: #ff0000 !important;
            color: white !important;
            font-weight: bold !important;
            font-size: 16px !important;
            padding: 12px 40px !important;
            border: 2px solid #ff0000 !important;
            border-radius: 8px !important;
            box-shadow: none !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
        }
        .glowing-button button:hover {
            background-color: #ff0000 !important;
            color: white !important;
            font-weight: bold !important;
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.8), 0 0 40px rgba(255, 0, 0, 0.6) !important;
            transform: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.markdown("<div class='glowing-button'>", unsafe_allow_html=True)
        if st.button("🚀 Proceed with Data Preparation", key="open_window", use_container_width=True):
            st.session_state.show_popup = True
        st.markdown("</div>", unsafe_allow_html=True)
    
    if st.session_state.get("show_popup", False):
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(
                    """
                    <div style='background-color: white; padding: 30px; border-radius: 10px; 
                    box-shadow: 0 4px 20px rgba(0,0,0,0.3); text-align: center;'>
                    <h3 style='color: #333;'>Data Preparation</h3>
                    <p style='color: #666;'>Your dataset is ready for processing and analysis.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                close_cols = st.columns([1, 1, 1])
                with close_cols[1]:
                    if st.button("Close", key="close_popup"):
                        st.session_state.show_popup = False
                        st.rerun()
