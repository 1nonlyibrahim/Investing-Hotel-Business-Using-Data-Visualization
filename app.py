#====================================================================
# IMPORT LIBRARY
#====================================================================================

import streamlit as st
import pandas as pd
#import numpy as np
#import plotly.express as px
#import plotly.graph_objects as go
#from PIL import Image
#import base64
#import os

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

    st.success("✅ Dataset uploaded successfully!")

    st.dataframe(df.head())