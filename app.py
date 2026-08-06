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
### Business Intelligence Platform

Analyze hotel booking behavior, cancellation trends,
customer insights, and revenue performance through
interactive visualizations.

---
""")

#====================================================================================
# FUNCTIONS TO LOAD THE BACKGROUND IMAGE
#====================================================================================

st.markdown("""
<div style="
background:rgba(255,255,255,0.08);
padding:25px;
border-radius:18px;
border:1px solid rgba(255,255,255,0.15);
backdrop-filter:blur(12px);
">

<h3 style="color:white;">Upload Dataset</h3>

</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload Hotel Booking CSV",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.success("✅ Dataset uploaded successfully!")

    st.dataframe(df.head())