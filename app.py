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

st.title("Hotel Booking Analytics Dashboard")

st.markdown("""
Analyze hotel booking behavior, cancellation trends,
customer insights, and revenue performance through
interactive visualizations.
---
""")

#====================================================================================
# FUNCTIONS TO LOAD THE BACKGROUND IMAGE
#====================================================================================

uploaded_file = st.file_uploader(
    "Upload Hotel Booking CSV",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.success("✅ Dataset uploaded successfully!")

    st.dataframe(df.head())