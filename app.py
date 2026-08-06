#====================================================================
# IMPORT LIBRARY
#====================================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import base64
import os

#====================================================================================
# STREAMLIT PAGE CONFIGURE
#====================================================================================

st.set_page_config(
    page_title="Hotel Booking Analytics Dashboard",
    page_icon="🛎️",
    layout="wide",
    init_sidebar_state="expanded"
)

#====================================================================================
# FUNCTIONS TO LOAD THE BACKGROUND IMAGE
#====================================================================================

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    st.markdown(
    f"""
        <style>

        /* Main App Background */
        .stApp {{
            background: linear-gradient(
                rgba(10, 25, 47, 0.80),
                rgba(10, 25, 47, 0.80)
            ),
            url("data:image/jpg;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background: rgba(15, 23, 42, 0.92);
        }}

        /* Metric Cards */
        div[data-testid="metric-container"] {{
            background-color: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 15px;
            padding: 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.25);
        }}

        /* Buttons */
        .stButton>button {{
            width:100%;
            border-radius:10px;
            font-weight:bold;
            background:#2E86DE;
            color:white;
        }}

        .stButton>button:hover {{
            background:#1B4F72;
            color:white;
        }}

        /* Headers */
        h1,h2,h3 {{
            color:white;
        }}

        p, label {{
            color:white;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )
# apply the image to the background
add_bg_from_local("C:\\Users\\admin\\Downloads\\apphotelbackground.jpg_semt=ais_hybrid&w=740&q=80")

#====================================================================================
# FUNCTIONS TO LOAD THE BACKGROUND IMAGE
#====================================================================================

#====================================================================================
# FUNCTIONS TO LOAD THE BACKGROUND IMAGE
#====================================================================================
