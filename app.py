#====================================================================================
# IMPORT LIBRARY
#====================================================================================

import streamlit as st
import pandas as pd
import numpy as np
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

-st.markdown(
    "<h1 style='text-align: center; text-transform: uppercase; color: white; font-weight: 700; font-size: 64px;'>Hotel Booking Analytics Dashboard</h1>", 
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

if "show_popup" not in st.session_state:
    st.session_state.show_popup = False

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



# ------------------------------------------------------------
# REQUIRED COLUMNS
# ------------------------------------------------------------

REQUIRED_COLUMNS = [
    "hotel",
    "is_canceled",
    "lead_time",
    "arrival_date_year",
    "arrival_date_month",
    "arrival_date_week_number",
    "arrival_date_day_of_month",
    "stays_in_weekend_nights",
    "stays_in_weekdays_nights",
    "adults",
    "children",
    "babies",
    "meal",
    "city",
    "market_segment",
    "distribution_channel",
    "is_repeated_guest",
    "previous_cancellations",
    "previous_bookings_not_canceled",
    "booking_changes",
    "deposit_type",
    "agent",
    "company",
    "days_in_waiting_list",
    "customer_type",
    "adr",
    "required_car_parking_spaces",
    "total_of_special_requests",
    "reservation_status"
]


# ============================================================
# RED GLOWING BUTTON
# ============================================================

if uploaded_file is not None:

    st.markdown(
        """
        <style>

        /* Main Streamlit button */
        div.stButton > button {

            background-color: #ff0000 !important;

            color: white !important;

            font-weight: 700 !important;

            font-size: 16px !important;

            border: 2px solid #ff0000 !important;

            border-radius: 8px !important;

            padding: 12px 30px !important;

            box-shadow: none !important;

            transition: all 0.3s ease-in-out !important;
        }

        /* Hover glow */
        div.stButton > button:hover {

            background-color: #ff0000 !important;

            color: white !important;

            border: 2px solid #ff0000 !important;

            box-shadow:
                0 0 10px rgba(255, 0, 0, 0.9),
                0 0 25px rgba(255, 0, 0, 0.8),
                0 0 45px rgba(255, 0, 0, 0.6) !important;

            transform: scale(1.02) !important;
        }

        /* Button click */
        div.stButton > button:active {

            transform: scale(0.98) !important;

        }

        </style>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # CENTER BUTTON
    # --------------------------------------------------------

    cols = st.columns([1, 2, 1])

    with cols[1]:

        proceed = st.button(
            "🚀 Proceed with Data Preparation",
            key="open_window",
            use_container_width=True
        )


    # ========================================================
    # DATA PREPARATION PIPELINE
    # ========================================================

    if proceed:

        # ----------------------------------------------------
        # READ DATA
        # ----------------------------------------------------

        df = pd.read_csv(uploaded_file)

        # Store original dataset
        original_df = df.copy()

        original_rows = len(df)
        original_columns = len(df.columns)


        # ====================================================
        # STEP 1 — COLUMN VALIDATION
        # ====================================================

        st.markdown("## 🔍 Dataset Validation")

        dataset_columns = set(df.columns)

        missing_columns = [
            column
            for column in REQUIRED_COLUMNS
            if column not in dataset_columns
        ]

        extra_columns = [
            column
            for column in df.columns
            if column not in REQUIRED_COLUMNS
        ]


        # ----------------------------------------------------
        # Missing required columns
        # ----------------------------------------------------

        if missing_columns:

            st.error(
                "❌ Dataset validation failed."
            )

            st.write("The following required columns are missing:")

            for column in missing_columns:
                st.write(f"❌ `{column}`")

            st.stop()


        else:

            st.success(
                f"✅ All {len(REQUIRED_COLUMNS)} required columns are available."
            )


        # ====================================================
        # STEP 2 — MISSING VALUES
        # ====================================================

        st.markdown("## 🧹 Missing Value Analysis")

        missing_before = df.isnull().sum()

        total_missing_before = missing_before.sum()

        missing_table = (
            missing_before[
                missing_before > 0
            ]
            .sort_values(ascending=False)
            .to_frame("Missing Values")
        )


        if total_missing_before > 0:

            st.warning(
                f"⚠️ {total_missing_before:,} missing values detected."
            )

            st.dataframe(
                missing_table,
                use_container_width=True
            )

        else:

            st.success(
                "✅ No missing values found."
            )


        # ====================================================
        # STEP 3 — HANDLE MISSING VALUES
        # ====================================================

        st.markdown("## 🔧 Handling Missing Values")


        # Numerical columns
        numerical_columns = [
            "lead_time",
            "arrival_date_year",
            "arrival_date_week_number",
            "arrival_date_day_of_month",
            "stays_in_weekend_nights",
            "stays_in_weekdays_nights",
            "adults",
            "children",
            "babies",
            "is_repeated_guest",
            "previous_cancellations",
            "previous_bookings_not_canceled",
            "booking_changes",
            "days_in_waiting_list",
            "adr",
            "required_car_parking_spaces",
            "total_of_special_requests"
        ]


        # Fill numerical missing values with median
        for column in numerical_columns:

            if column in df.columns:

                if df[column].isnull().sum() > 0:

                    df[column] = df[column].fillna(
                        df[column].median()
                    )


        # Categorical columns
        categorical_columns = [
            "hotel",
            "arrival_date_month",
            "meal",
            "city",
            "market_segment",
            "distribution_channel",
            "deposit_type",
            "customer_type",
            "reservation_status"
        ]


        # Fill categorical missing values with mode
        for column in categorical_columns:

            if column in df.columns:

                if df[column].isnull().sum() > 0:

                    mode_value = df[column].mode()

                    if not mode_value.empty:

                        df[column] = df[column].fillna(
                            mode_value[0]
                        )


        # Agent and company
        # Missing means no agent/company was assigned.
        if "agent" in df.columns:

            df["agent"] = df["agent"].fillna(0)


        if "company" in df.columns:

            df["company"] = df["company"].fillna(0)


        # ====================================================
        # STEP 4 — REMOVE DUPLICATES
        # ====================================================

        st.markdown("## 🗑️ Duplicate Analysis")

        duplicates_before = df.duplicated().sum()

        if duplicates_before > 0:

            df = df.drop_duplicates()

            st.success(
                f"✅ Removed {duplicates_before:,} duplicate rows."
            )

        else:

            st.success(
                "✅ No duplicate rows found."
            )


        # ====================================================
        # STEP 5 — FIX DATA TYPES
        # ====================================================

        st.markdown("## 🔄 Data Type Conversion")


        integer_columns = [
            "is_canceled",
            "lead_time",
            "arrival_date_year",
            "arrival_date_week_number",
            "arrival_date_day_of_month",
            "stays_in_weekend_nights",
            "stays_in_weekdays_nights",
            "adults",
            "children",
            "babies",
            "is_repeated_guest",
            "previous_cancellations",
            "previous_bookings_not_canceled",
            "booking_changes",
            "days_in_waiting_list",
            "required_car_parking_spaces",
            "total_of_special_requests"
        ]


        for column in integer_columns:

            if column in df.columns:

                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce"
                ).fillna(0).astype(int)


        # ADR should be float
        if "adr" in df.columns:

            df["adr"] = pd.to_numeric(
                df["adr"],
                errors="coerce"
            )


        # Agent and company
        if "agent" in df.columns:

            df["agent"] = pd.to_numeric(
                df["agent"],
                errors="coerce"
            ).fillna(0).astype(int)


        if "company" in df.columns:

            df["company"] = pd.to_numeric(
                df["company"],
                errors="coerce"
            ).fillna(0).astype(int)


        # ====================================================
        # STEP 6 — DATA VALIDATION
        # ====================================================

        st.markdown("## ✅ Final Data Validation")


        remaining_missing = df.isnull().sum().sum()

        remaining_duplicates = df.duplicated().sum()

        final_rows = len(df)


        col1, col2, col3, col4 = st.columns(4)


        col1.metric(
            "Original Rows",
            f"{original_rows:,}"
        )


        col2.metric(
            "Final Rows",
            f"{final_rows:,}"
        )


        col3.metric(
            "Missing Values",
            f"{remaining_missing:,}"
        )


        col4.metric(
            "Duplicate Rows",
            f"{remaining_duplicates:,}"
        )


        # ====================================================
        # FINAL RESULT
        # ====================================================

        if remaining_missing == 0 and remaining_duplicates == 0:

            st.success(
                "🎉 Data preparation completed successfully!"
            )

        else:

            st.warning(
                "⚠️ Some data quality issues still remain."
            )


        # ====================================================
        # SAVE CLEANED DATA
        # ====================================================

        st.session_state["cleaned_df"] = df

        st.session_state["original_df"] = original_df

        st.session_state["data_prepared"] = True


        # ====================================================
        # CLEANING SUMMARY
        # ====================================================

        st.markdown("## 📊 Cleaning Summary")

        summary_col1, summary_col2 = st.columns(2)


        with summary_col1:

            st.write(
                f"**Original Rows:** {original_rows:,}"
            )

            st.write(
                f"**Duplicate Rows Removed:** "
                f"{duplicates_before:,}"
            )

            st.write(
                f"**Final Rows:** {final_rows:,}"
            )


        with summary_col2:

            st.write(
                f"**Original Missing Values:** "
                f"{total_missing_before:,}"
            )

            st.write(
                f"**Remaining Missing Values:** "
                f"{remaining_missing:,}"
            )

            st.write(
                f"**Columns:** {original_columns}"
            )


        # ====================================================
        # SHOW CLEANED DATA
        # ====================================================

        with st.expander("👀 Preview Cleaned Dataset"):

            st.dataframe(
                df.head(100),
                use_container_width=True
            )