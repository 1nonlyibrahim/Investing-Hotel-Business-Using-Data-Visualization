#=========================================================================================================================================================================================================
# IMPORT LIBRARY
#=========================================================================================================================================================================================================

import streamlit as st
import pandas as pd
import numpy as np
import hashlib
import time
import base64
import plotly.express as px

from hotel_booking_analytics_dashboard import render_executive_overview

#=========================================================================================================================================================================================================
# STREAMLIT PAGE CONFIGURE
#=========================================================================================================================================================================================================

st.set_page_config(
    page_title="Hotel Booking Analytics Dashboard",
    page_icon="🛎️",
    layout="wide",
)

#=========================================================================================================================================================================================================
# ALL THE DEF FUNCTIONS ARE DEFINED HERE
#=========================================================================================================================================================================================================
def show_notification(message, duration=3):
    st.markdown(
        f"""
        <style>
        .custom-notification{{position:fixed;top:75px;left:50%;transform:translateX(-50%);z-index:999999;min-width:380px;max-width:650px;padding:15px 24px;background:rgba(5,35,20,.97);border:1px solid #20ff8a;border-radius:12px;color:#20ff8a;font-size:15px;font-weight:600;letter-spacing:.2px;display:flex;align-items:center;justify-content:center;text-align:center;animation:notification-slide-down .5s ease-out forwards,notification-slide-up .5s ease-in {duration}s forwards;pointer-events:none}}
        @keyframes notification-slide-down{{0%{{opacity:0;transform:translate(-50%,-12px)}}100%{{opacity:1;transform:translate(-50%,0)}}}}
        @keyframes notification-slide-up{{0%{{opacity:1;transform:translate(-50%,0)}}100%{{opacity:0;transform:translate(-50%,-12px)}}}}
        </style>
        <div class="custom-notification">{message}</div>
        """,
        unsafe_allow_html=True,
    )

st.session_state.setdefault("pending_notification", None)
if st.session_state.get("pending_notification"):
    msg = st.session_state.pending_notification
    st.session_state.pending_notification = None
    show_notification(msg)

#====================================================================================

def get_uploaded_file_id(uploaded_file):
    if uploaded_file is None:
        return None
    uploaded_file.seek(0)
    file_bytes = uploaded_file.getvalue()
    return None if not file_bytes else f"{uploaded_file.name}:{uploaded_file.size}:{hashlib.md5(file_bytes).hexdigest()}"


def render_preparation_popup(step_index, total_steps, status, detail, title="Preparing your dataset", current_step_name=None):
    st.session_state.prep_popup_visible = True
    st.session_state.prep_popup_step_index = step_index
    st.session_state.prep_popup_total_steps = total_steps
    st.session_state.prep_popup_status = status
    st.session_state.prep_popup_detail = detail
    st.session_state.prep_popup_title = title
    st.session_state.prep_popup_current_step_name = current_step_name

    progress_percent = 100 if status == "success" else max(8, int(((step_index + 1) / total_steps) * 100))
    step_names = ["Validate required columns", "Check missing values", "Remove duplicate rows", "Fix data types", "Finalize dataset"]
    status_styles = {
        "running": ("⏳", "background:#f8fafc;color:#0f172a;border:1px solid #dbe4f0;"),
        "success": ("✅", "background:#ecfdf3;color:#166534;border:1px solid #a7f3d0;"),
        "error": ("❌", "background:#fef2f2;color:#b91c1c;border:1px solid #fecaca;"),
    }
    default_style = "background:#fff;color:#64748b;border:1px solid #e2e8f0;"
    step_items = []
    for idx, step_name in enumerate(step_names):
        icon, style = status_styles["success"] if idx < step_index else status_styles[status] if idx == step_index else ("○", default_style)
        step_items.append(f"<div style='margin-top:10px;padding:12px 14px;border-radius:10px;{style}'>{icon} <strong>{step_name}</strong></div>")

    message_box = {
        "error": f"<div style='margin-top:16px;padding:12px 14px;border-radius:10px;background:#fee2e2;color:#991b1b;border:1px solid #fecaca;'>{detail}</div>",
        "success": f"<div style='margin-top:16px;padding:12px 14px;border-radius:10px;background:#ecfdf3;color:#166534;border:1px solid #a7f3d0;'>{detail}</div>",
    }.get(status, f"<div style='margin-top:16px;padding:12px 14px;border-radius:10px;background:#f8fafc;color:#0f172a;border:1px solid #dbe4f0;'>{detail}</div>")

    current_label = current_step_name or (step_names[step_index] if step_index < len(step_names) else "Finishing up")

    html = f"""
    <div style="position:fixed;inset:0;z-index:9999;background:rgba(15,23,42,.72);display:flex;align-items:center;justify-content:center;padding:24px;">
      <div style="width:min(780px,100%);background:rgba(255,255,255,.97);border-radius:18px;padding:24px 28px;box-shadow:0 20px 60px rgba(0,0,0,.35);border:1px solid rgba(255,255,255,.25);">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;">
          <div>
            <h3 style="margin:0 0 8px;color:#111827;font-size:24px;">{title}</h3>
            <p style="margin:0;color:#4b5563;">Please wait while we prepare your dataset.</p>
          </div>
          <div style="padding:8px 12px;border-radius:999px;background:#f3f4f6;color:#374151;font-size:13px;font-weight:700;">{current_label}</div>
        </div>
        <div style="position:relative;height:10px;width:100%;background:#e5e7eb;border-radius:999px;overflow:hidden;margin-top:14px;">
          <div style="height:100%;width:{progress_percent}%;background:linear-gradient(90deg,#ef4444,#f59e0b,#10b981);border-radius:999px;animation:pulse 1.2s ease-in-out infinite;"></div>
        </div>
        <div style="margin-top:16px;">{''.join(step_items)}</div>
        {message_box}
      </div>
    </div>
    <style>
    @keyframes pulse {{
      0%, 100% {{ opacity: 0.9; transform: scaleX(1); }}
      50% {{ opacity: 1; transform: scaleX(1.01); }}
    }}
    </style>
    """
    st.markdown(html, unsafe_allow_html=True)


def set_background_image(image_path):
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode()
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"]{{position:relative;isolation:isolate;background:transparent}}
        [data-testid="stAppViewContainer"]::before{{content:"";position:fixed;inset:0;background-image:url("data:image/png;base64,{image_data}");background-size:cover;background-position:center;background-repeat:no-repeat;background-attachment:fixed;filter:blur(8px);transform:scale(1.05);z-index:-1;pointer-events:none}}
        [data-testid="stAppViewContainer"] > *{{position:relative;z-index:1}}
        </style>
        """,
        unsafe_allow_html=True,
    )


set_background_image("Abstract red to black gradient background with grainy noise texture for digital design projects.jfif")

#=========================================================================================================================================================================================================
# HEADER AND INTRO SECTION
#=========================================================================================================================================================================================================

st.markdown(
    "<h1 style='text-align: center; text-transform: uppercase; color: white; font-weight: 700; font-size: 64px;'>Hotel Booking Insights Dashboard</h1>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="text-align:center; max-width:800px; margin:auto;">

    <p style="font-size:17px; color:#bdbdbd; line-height:1.7;">
    An interactive Business Intelligence dashboard for analyzing hotel
    booking behavior, cancellation patterns, customer trends, pricing,
    lead time, stay duration, and estimated revenue.
    Upload your hotel booking dataset and transform raw data into
    meaningful insights and actionable business recommendations.
    </p>

    </div>
    """,
    unsafe_allow_html=True
)

#=========================================================================================================================================================================================================
# UPLOADER BOX
#=========================================================================================================================================================================================================

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
    type=["csv"],
    key="dataset_uploader",
)

if uploaded_file is None:
    st.session_state["uploaded_file"] = None
    st.session_state["uploaded_file_name"] = None
    st.session_state["uploaded_file_id"] = None
    st.session_state["raw_df"] = None
    st.session_state["cleaned_df"] = None
    st.session_state["original_df"] = None
    st.session_state["data_prepared"] = False
    st.session_state["show_processing"] = False
    st.session_state["prep_popup_visible"] = False
else:
    st.session_state["uploaded_file"] = uploaded_file
    current_file_id = get_uploaded_file_id(uploaded_file)
    previous_file_id = st.session_state.get("uploaded_file_id")

    if current_file_id != previous_file_id:
        st.session_state["uploaded_file_id"] = current_file_id
        st.session_state["uploaded_file_name"] = uploaded_file.name
        st.session_state["data_prepared"] = False
        st.session_state["show_processing"] = False
        st.session_state["prep_popup_visible"] = False
        st.session_state["cleaned_df"] = None
        st.session_state["original_df"] = None

        try:
            uploaded_file.seek(0)
            raw_df = pd.read_csv(
                uploaded_file,
                encoding="utf-8",
                encoding_errors="replace",
                low_memory=False,
            )
            st.session_state["raw_df"] = raw_df
            show_notification("📄 Dataset selected. Click below to begin preparation.")
        except Exception:
            try:
                uploaded_file.seek(0)
                raw_df = pd.read_csv(
                    uploaded_file,
                    encoding="latin-1",
                    low_memory=False,
                )
                st.session_state["raw_df"] = raw_df
                show_notification("📄 Dataset selected. Click below to begin preparation.")
            except Exception as e:
                st.session_state["raw_df"] = None
                st.error("❌ Could not read the uploaded CSV file.")
                st.caption("Please make sure the uploaded file is a valid CSV and uses the expected Hotel Booking dataset format.")
                st.session_state["prep_popup_visible"] = False
                st.session_state["show_processing"] = False
                st.session_state["data_prepared"] = False
                st.code(str(e))
    else:
        st.session_state["uploaded_file_name"] = uploaded_file.name

#=========================================================================================================================================================================================================
#DATA PREPARATION BUTTON
#=========================================================================================================================================================================================================

# ------------------------------------------------------------
# REQUIRED HOTEL BOOKING COLUMNS
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
    "reservation_status",
]

NUMERIC_COLUMNS = [
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
    "adr",
    "required_car_parking_spaces",
    "total_of_special_requests",
]

STRING_COLUMNS = [
    "hotel",
    "arrival_date_month",
    "meal",
    "market_segment",
    "distribution_channel",
    "deposit_type",
    "customer_type",
    "reservation_status",
]

PREP_STEP_LABELS = [
    ("Checking required columns", "Required columns verified"),
    ("Removing missing data", "Missing data removed"),
    ("Removing duplicate records", "Duplicate records removed"),
    ("Fixing column data types", "Data types corrected"),
]


# ------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------

for key, value in {
    "preparation_running": False,
    "preparation_complete": False,
    "prepared_df": None,
    "original_df": None,
    "preparation_stats": {},
}.items():
    st.session_state.setdefault(key, value)


# ------------------------------------------------------------
# BUTTON CSS
# ------------------------------------------------------------

st.markdown(
    """
    <style>
    div.stButton > button.prepare-data-btn {
        background-color: #e60000 !important;
        color: white !important;
        border: 2px solid #ff1a1a !important;
        border-radius: 10px !important;
        padding: 13px 35px !important;
        font-size: 17px !important;
        font-weight: 700 !important;
        letter-spacing: 0.3px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 0 rgba(255, 0, 0, 0) !important;
    }
    div.stButton > button.prepare-data-btn:hover {
        background-color: #ff1111 !important;
        color: white !important;
        border-color: #ff3333 !important;
        box-shadow:
            0 0 10px rgba(255, 0, 0, 0.9),
            0 0 25px rgba(255, 0, 0, 0.8),
            0 0 45px rgba(255, 0, 0, 0.55) !important;
        transform: translateY(-2px) !important;
    }
    .prep-container {
        max-width: 650px;
        margin: 25px auto;
        padding: 25px 30px;
        border-radius: 15px;
        background: rgba(20, 20, 20, 0.92);
        border: 1px solid rgba(255, 0, 0, 0.35);
        box-shadow:
            0 0 15px rgba(255, 0, 0, 0.15),
            inset 0 0 20px rgba(255, 0, 0, 0.03);
    }
    .prep-title {
        text-align: center;
        color: white;
        font-size: 21px;
        font-weight: 700;
        margin-bottom: 18px;
    }
    .prep-step {
        color: #bdbdbd;
        font-size: 15px;
        padding: 9px 0;
    }
    .prep-active {
        color: #ff3333;
        font-weight: 700;
    }
    .prep-complete {
        color: #42ff75;
        font-weight: 600;
    }
    .prep-final {
        text-align: center;
        color: #ff3333;
        font-size: 15px;
        font-weight: 700;
        margin-top: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# ONLY SHOW BUTTON AFTER FILE IS UPLOADED
# ------------------------------------------------------------

def render_prep_status(container, title, active_step=None, completed_steps=None):
    completed_steps = completed_steps or []
    html = [f'<div class="prep-container">', f'<div class="prep-title">{title}</div>']
    for i, (active_label, complete_label) in enumerate(PREP_STEP_LABELS, 1):
        if i in completed_steps:
            css, prefix, label = "prep-complete", "✓", complete_label
        elif active_step is not None and i == active_step:
            css, prefix, label = "prep-active", "●", active_label
        else:
            css, prefix, label = "", "○", active_label
        cls = f' {css}' if css else ""
        html.append(f'<div class="prep-step{cls}">{prefix} Step {i} — {label}</div>')
    html.append('<div class="prep-final">Processing data for analysis…</div></div>')
    container.markdown("\n".join(html), unsafe_allow_html=True)


st.session_state.setdefault("preparation_running", False)
st.session_state.setdefault("preparation_complete", False)

if uploaded_file is not None:
    if not st.session_state["preparation_running"] and not st.session_state["preparation_complete"]:
        st.markdown(
            """
            <style>
            div[data-testid="stButton"] > button {
                background: #e60000 !important;
                color: #ffffff !important;
                border: 2px solid #ff2222 !important;
                border-radius: 10px !important;
                font-size: 17px !important;
                font-weight: 700 !important;
                padding: 12px 32px !important;
                transition: background 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease !important;
                box-shadow: 0 0 0 rgba(255, 0, 0, 0) !important;
            }
            div[data-testid="stButton"] > button:hover {
                background: #ff0000 !important;
                color: #ffffff !important;
                border: 2px solid #ff5555 !important;
                box-shadow:
                    0 0 8px #ff0000,
                    0 0 18px #ff0000,
                    0 0 35px rgba(255, 0, 0, 0.9),
                    0 0 60px rgba(255, 0, 0, 0.6) !important;
                transform: translateY(-2px) !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            prepare_clicked = st.button(
                "⚡ Validate & Prepare Data",
                key="validate_prepare_button",
                width="stretch",
            )

        if prepare_clicked:
            st.session_state["preparation_running"] = True
            st.rerun()

    if st.session_state["preparation_running"]:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file)
            
        except Exception as e:
            st.session_state["preparation_running"] = False
            st.error(f"Unable to read the uploaded CSV file.\n\n{e}")
            st.stop()

        original_df = df.copy()
        st.session_state["original_df"] = original_df

        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_status(title, active_step=None, completed_steps=None):
            render_prep_status(
                status_text,
                title,
                active_step=active_step,
                completed_steps=completed_steps,
            )
            time.sleep(0.7)

        update_status("🔍 Validating your dataset", active_step=1)

        missing_columns = [column for column in REQUIRED_COLUMNS if column not in set(df.columns)]
        if missing_columns:
            progress_bar.empty()
            status_text.error(
                "❌ Dataset validation failed.\n\n"
                "The following required columns are missing:\n\n"
                + "\n".join(f"• {column}" for column in missing_columns)
            )
            st.session_state["preparation_running"] = False
            st.stop()

        progress_bar.progress(25)
        update_status("🧹 Preparing your dataset", active_step=2, completed_steps=[1])
        rows_before_missing = len(df)

        critical_columns = [
            "hotel",
            "is_canceled",
            "lead_time",
            "arrival_date_year",
            "arrival_date_month",
            "arrival_date_day_of_month",
            "adr"
        ]
        df = df.dropna(subset=critical_columns).copy()
        missing_rows_removed = rows_before_missing - len(df)
        progress_bar.progress(50)

        update_status("🧹 Preparing your dataset", active_step=3, completed_steps=[1, 2])
        rows_before_duplicates = df.duplicated().sum()
        df = df.drop_duplicates().copy()
        duplicate_rows_removed = rows_before_duplicates
        progress_bar.progress(75)

        update_status("⚙️ Finalizing your dataset", active_step=4, completed_steps=[1, 2, 3])
        for column in NUMERIC_COLUMNS:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors="coerce")
        for column in STRING_COLUMNS:
            if column in df.columns:
                df[column] = df[column].astype("string")

        progress_bar.progress(100)
        time.sleep(0.8)

        st.session_state["preparation_stats"] = {
            "original_rows": len(original_df),
            "final_rows": len(df),
            "original_columns": len(original_df.columns),
            "final_columns": len(df.columns),
            "missing_rows_removed": missing_rows_removed,
            "duplicate_rows_removed": duplicate_rows_removed,
            "remaining_missing_values": int(df.isna().sum().sum()),
            "remaining_duplicates": int(df.duplicated().sum()),
        }
    
        prepared_df = df.copy()
        st.session_state["prepared_df"] = prepared_df

        render_prep_status(
            status_text,
            "✅ Dataset preparation complete",
            completed_steps=[1, 2, 3, 4],
        )
        time.sleep(1)

        progress_bar.empty()
        status_text.empty()
        st.session_state["preparation_running"] = False
        st.session_state["preparation_complete"] = True
        st.rerun()

    if st.session_state["preparation_complete"]:
        pass

#=========================================================================================================================================================================================================
# SIDEBAR — NAVIGATION + PREPARED DATASET INFORMATION
#=========================================================================================================================================================================================================

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        overflow-y: auto !important;
        max-height: 100vh !important;
    }
    [data-testid="stSidebarContent"] {
        overflow-y: auto !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:

    # --------------------------------------------------------
    # 1. ANALYSIS NAVIGATION
    # --------------------------------------------------------

    analysis_pages = [
        "📊 Executive Overview",
        "🏨 Hotel Performance",
        "📅 Booking Trends",
        "❌ Cancellation Analysis",
        "⏳ Lead Time Analysis",
        "🛏️ Stay Duration",
        "💰 Revenue Analysis",
        "👥 Customer & Market Analysis",
        "🔎 Relationship Analysis",
        "📌 Business Insights",
        "💡 Recommendations",
    ]

    st.markdown(
        "<div style='font-size:30px;font-weight:700;text-align:center;margin-bottom:8px;'>📊 Analysis</div>",
        unsafe_allow_html=True,
    )

    selected_page = st.selectbox(
        "Select Analysis Page from the dropdown list below:",
        analysis_pages,
        key="selected_analysis_page",
    )

    # --------------------------------------------------------
    # DIVIDER
    # --------------------------------------------------------

    st.divider()

    # --------------------------------------------------------
    # 2. PREPARED DATASET INFORMATION
    # --------------------------------------------------------

    st.markdown(
        "<div style='font-size:30px;font-weight:700;text-align:center;margin-bottom:10px;'>📋 Prepared Dataset</div>",
        unsafe_allow_html=True,
    )

    prepared_df = st.session_state.get("prepared_df")

    with st.expander("📊 Dataset Information", expanded=False):
        if prepared_df is not None:
            st.metric("Rows", f"{len(prepared_df):,}")
            st.metric("Columns", f"{len(prepared_df.columns):,}")
            st.metric("Missing Values", f"{int(prepared_df.isna().sum().sum()):,}")
            st.metric("Duplicate Rows", f"{int(prepared_df.duplicated().sum()):,}")
        else:
            st.info("Prepare the dataset first to view dataset information.")

    # --------------------------------------------------------
    # DATASET PREVIEW
    # --------------------------------------------------------

    with st.expander("👁️ Dataset Preview", expanded=False):
        if prepared_df is not None:
            st.dataframe(prepared_df.head(10), width="stretch", hide_index=True)
        else:
            st.info("Dataset preview will appear after preparation.")

    # --------------------------------------------------------
    # DIVIDER
    # --------------------------------------------------------

    st.divider()

    # --------------------------------------------------------
    # 3. DATA PREPARATION INFORMATION
    # --------------------------------------------------------

    st.markdown(
        """
        <div style='font-size:30px;font-weight:700;text-align:center;margin-bottom:6px;'>🧹 Data Preparation</div>
        <div style='font-size:13px;color:#999999;line-height:1.5;margin-bottom:12px;'>
            This section shows how the uploaded dataset was validated and prepared before analysis.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # PREPARATION SUMMARY
    # --------------------------------------------------------

    with st.expander("🔍 Preparation Summary", expanded=False):
        stats = st.session_state.get("preparation_stats", {})

        if stats:
            st.markdown("**📥 Original Dataset**")
            st.write(f"Rows: **{stats.get('original_rows', 0):,}**")
            st.write(f"Columns: **{stats.get('original_columns', 0):,}**")
            st.divider()

            st.markdown("**⚙️ Preparation Performed**")
            st.markdown("✅ Required columns verified")
            st.markdown(
                f"✅ Missing-data rows removed: **{stats.get('missing_rows_removed', 0):,}**"
            )
            st.markdown(
                f"✅ Duplicate rows removed: **{stats.get('duplicate_rows_removed', 0):,}**"
            )
            st.markdown("✅ Column data types corrected")
            st.divider()

            st.markdown("**📤 Final Prepared Dataset**")
            st.write(f"Rows: **{stats.get('final_rows', 0):,}**")
            st.write(f"Columns: **{stats.get('final_columns', 0):,}**")
            st.write(
                f"Remaining missing values: **{stats.get('remaining_missing_values', 0):,}**"
            )
            st.write(f"Remaining duplicates: **{stats.get('remaining_duplicates', 0):,}**")
        else:
            st.info("Preparation statistics will appear after the dataset has been prepared.")

    # --------------------------------------------------------
    # WHAT WAS DONE
    # --------------------------------------------------------

    with st.expander("📝 What Was Done?", expanded=False):
        st.markdown(
            """
            **The dataset preparation process includes:**

            **1. Column Validation**  
            Required columns were checked to ensure that the uploaded dataset contains the fields needed for analysis.

            **2. Missing Data Removal**  
            Rows containing missing data were removed.

            **3. Duplicate Removal**  
            Duplicate records were identified and removed.

            **4. Data Type Correction**  
            Numerical and categorical columns were converted to appropriate data types.

            **5. Analysis Preparation**  
            The cleaned dataset was stored and made ready for the dashboard's analysis and visualizations.
            """
        )

#===========================================================================================================================================================================================================
# EXECUTIVE OVERVIEW PAGE
#===========================================================================================================================================================================================================

def render_executive_overview_page(df):
   if df is None or df.empty:
    st.info("📂 Please upload and prepare your dataset first.")
    return
# Work with a copy so the original prepared dataset
    # is never modified by this page.
    data = df.copy()

    # --------------------------------------------------------
    # CREATE REQUIRED CALCULATED COLUMNS
    # --------------------------------------------------------

    # Total stay duration
    if (
        "stays_in_weekend_nights" in data.columns
        and "stays_in_week_nights" in data.columns
    ):
        data["total_stay_nights"] = (
            pd.to_numeric(
                data["stays_in_weekend_nights"],
                errors="coerce"
            ).fillna(0)
            +
            pd.to_numeric(
                data["stays_in_week_nights"],
                errors="coerce"
            ).fillna(0)
        )

    else:
        data["total_stay_nights"] = 0

    # Estimated revenue
    if "adr" in data.columns:
        data["estimated_revenue"] = (
            pd.to_numeric(
                data["adr"],
                errors="coerce"
            ).fillna(0)
            *
            data["total_stay_nights"]
        )
    else:
        data["estimated_revenue"] = 0

    # --------------------------------------------------------
    # MONTH ORDER
    # --------------------------------------------------------

    month_order = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December"
    ]

    # --------------------------------------------------------
    # PAGE HEADER
    # --------------------------------------------------------

    st.markdown(
        """
        <style>
        html, body, [class*="st-"] {
            color: white !important;
        }

        h1, h2, h3, h4, h5, h6 {
            color: white !important;
            font-weight: bold !important;
        }

        [data-testid="stMetricLabel"] {
            color: white !important;
            font-weight: bold !important;
        }

        [data-testid="stMetricValue"] {
            color: white !important;
            font-weight: normal !important;
        }

        .stAlert, .stInfo, .stSuccess, .stWarning {
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "<h2 style='color: white; font-weight: bold; margin-bottom: 0.25rem;'>Executive Overview</h2>"
        "<p style='color: white; font-weight: normal; margin-top: 0;'>High-level overview of hotel booking performance, demand, cancellations and revenue.</p>",
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # BASIC VALUES
    # --------------------------------------------------------

    total_bookings = len(data)

    if "is_canceled" in data.columns:

        canceled_bookings = int(
            pd.to_numeric(
                data["is_canceled"],
                errors="coerce"
            ).fillna(0).sum()
        )

        confirmed_bookings = (
            total_bookings - canceled_bookings
        )

    else:

        canceled_bookings = 0
        confirmed_bookings = total_bookings

    cancellation_rate = (
        canceled_bookings / total_bookings * 100
        if total_bookings > 0
        else 0
    )

    # Average ADR
    average_adr = (
        pd.to_numeric(
            data["adr"],
            errors="coerce"
        ).mean()
        if "adr" in data.columns
        else 0
    )

    # Average lead time
    average_lead_time = (
        pd.to_numeric(
            data["lead_time"],
            errors="coerce"
        ).mean()
        if "lead_time" in data.columns
        else 0
    )

    # Average stay
    average_stay = (
        data["total_stay_nights"].mean()
        if len(data) > 0
        else 0
    )

    # Revenue
    total_revenue = data["estimated_revenue"].sum()

    # Revenue lost from cancellations
    if "is_canceled" in data.columns:

        cancelled_revenue = data.loc[
            pd.to_numeric(
                data["is_canceled"],
                errors="coerce"
            ).fillna(0) == 1,
            "estimated_revenue"
        ].sum()

    else:

        cancelled_revenue = 0

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    st.markdown(
        "<h3 style='color: white; font-weight: bold; margin-bottom: 0.5rem;'>📌 Key Performance Indicators</h3>",
        unsafe_allow_html=True
    )

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.metric(
            "Total Bookings",
            f"{total_bookings:,}"
        )

    with kpi2:
        st.metric(
            "Confirmed Bookings",
            f"{confirmed_bookings:,}"
        )

    with kpi3:
        st.metric(
            "Cancelled Bookings",
            f"{canceled_bookings:,}"
        )

    with kpi4:
        st.metric(
            "Cancellation Rate",
            f"{cancellation_rate:.1f}%"
        )

    kpi5, kpi6, kpi7, kpi8 = st.columns(4)

    with kpi5:
        st.metric(
            "Average ADR",
            f"{average_adr:,.2f}"
        )

    with kpi6:
        st.metric(
            "Average Lead Time",
            f"{average_lead_time:,.1f} days"
        )

    with kpi7:
        st.metric(
            "Average Stay",
            f"{average_stay:,.1f} nights"
        )

    with kpi8:
        st.metric(
            "Estimated Revenue",
            f"{total_revenue:,.0f}"
        )

    st.metric(
        "Revenue Lost from Cancellations",
        f"{cancelled_revenue:,.0f}"
    )

    st.divider()

    # --------------------------------------------------------
    # ROW 1 — HOTEL + MONTHLY BOOKINGS
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # BOOKINGS BY HOTEL
    # --------------------------------------------------------

    with col1:

        st.markdown(
            "<h3 style='color: white; font-weight: bold;'>🏨 Bookings by Hotel</h3>",
            unsafe_allow_html=True
        )

        if "hotel" in data.columns:

            hotel_counts = (
                data["hotel"]
                .value_counts()
                .reset_index()
            )

            hotel_counts.columns = [
                "Hotel",
                "Bookings"
            ]

            fig_hotel = px.pie(
                hotel_counts,
                names="Hotel",
                values="Bookings",
                hole=0.55
            )

            fig_hotel.update_layout(
                margin=dict(
                    l=10,
                    r=10,
                    t=20,
                    b=10
                ),
                legend_title=""
            )

            st.plotly_chart(
                fig_hotel,
                width="stretch"
            )

        else:

            st.info(
                "Hotel column is not available."
            )

    # --------------------------------------------------------
    # MONTHLY BOOKINGS
    # --------------------------------------------------------

    with col2:

        st.markdown(
            "<h3 style='color: white; font-weight: bold;'>📅 Monthly Bookings</h3>",
            unsafe_allow_html=True
        )

        if (
            "arrival_date_month" in data.columns
        ):

            monthly = (
                data["arrival_date_month"]
                .value_counts()
                .reindex(
                    month_order,
                    fill_value=0
                )
                .reset_index()
            )

            monthly.columns = [
                "Month",
                "Bookings"
            ]

            fig_month = px.line(
                monthly,
                x="Month",
                y="Bookings",
                markers=True
            )

            fig_month.update_layout(
                margin=dict(
                    l=10,
                    r=10,
                    t=20,
                    b=10
                ),
                xaxis_title="",
                yaxis_title="Bookings"
            )

            st.plotly_chart(
                fig_month,
                width="stretch"
            )

        else:

            st.info(
                "Arrival month column is not available."
            )

    # --------------------------------------------------------
    # ROW 2 — CANCELLATION + ADR
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # MONTHLY CANCELLATION RATE
    # --------------------------------------------------------

    with col1:

        st.markdown(
            "<h3 style='color: white; font-weight: bold;'>❌ Monthly Cancellation Rate</h3>",
            unsafe_allow_html=True
        )

        if (
            "arrival_date_month" in data.columns
            and "is_canceled" in data.columns
        ):

            cancellation_month = (
                data.groupby(
                    "arrival_date_month"
                )["is_canceled"]
                .mean()
                .reindex(month_order)
                .fillna(0)
                .reset_index()
            )

            cancellation_month.columns = [
                "Month",
                "Cancellation Rate"
            ]

            cancellation_month[
                "Cancellation Rate"
            ] *= 100

            fig_cancel = px.line(
                cancellation_month,
                x="Month",
                y="Cancellation Rate",
                markers=True
            )

            fig_cancel.update_layout(
                margin=dict(
                    l=10,
                    r=10,
                    t=20,
                    b=10
                ),
                xaxis_title="",
                yaxis_title="Cancellation Rate (%)"
            )

            st.plotly_chart(
                fig_cancel,
                width="stretch"
            )

        else:

            st.info(
                "Cancellation or month data is unavailable."
            )

    # --------------------------------------------------------
    # MONTHLY ADR
    # --------------------------------------------------------

    with col2:

        st.markdown(
            "<h3 style='color: white; font-weight: bold;'>💰 Average ADR by Month</h3>",
            unsafe_allow_html=True
        )

        if (
            "arrival_date_month" in data.columns
            and "adr" in data.columns
        ):

            monthly_adr = (
                data.groupby(
                    "arrival_date_month"
                )["adr"]
                .mean()
                .reindex(month_order)
                .reset_index()
            )

            monthly_adr.columns = [
                "Month",
                "Average ADR"
            ]

            fig_adr = px.line(
                monthly_adr,
                x="Month",
                y="Average ADR",
                markers=True
            )

            fig_adr.update_layout(
                margin=dict(
                    l=10,
                    r=10,
                    t=20,
                    b=10
                ),
                xaxis_title="",
                yaxis_title="Average ADR"
            )

            st.plotly_chart(
                fig_adr,
                width="stretch"
            )

        else:

            st.info(
                "ADR or month data is unavailable."
            )

    st.divider()

    # --------------------------------------------------------
    # ROW 3 — MARKET SEGMENT
    # --------------------------------------------------------

    st.markdown(
        "<h3 style='color: white; font-weight: bold;'>📢 Booking Distribution</h3>",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # MARKET SEGMENT
    # --------------------------------------------------------

    with col1:

        st.markdown(
            "<h4 style='color: white; font-weight: bold;'>Market Segment</h4>",
            unsafe_allow_html=True
        )

        if "market_segment" in data.columns:

            market_counts = (
                data["market_segment"]
                .value_counts()
                .reset_index()
            )

            market_counts.columns = [
                "Market Segment",
                "Bookings"
            ]

            fig_market = px.bar(
                market_counts,
                x="Bookings",
                y="Market Segment",
                orientation="h"
            )

            fig_market.update_layout(
                margin=dict(
                    l=10,
                    r=10,
                    t=20,
                    b=10
                ),
                xaxis_title="Bookings",
                yaxis_title=""
            )

            st.plotly_chart(
                fig_market,
                width="stretch"
            )

        else:

            st.info(
                "Market segment data is unavailable."
            )

    # --------------------------------------------------------
    # CUSTOMER TYPE
    # --------------------------------------------------------

    with col2:

        st.markdown(
            "<h4 style='color: white; font-weight: bold;'>Customer Type</h4>",
            unsafe_allow_html=True
        )

        if "customer_type" in data.columns:

            customer_counts = (
                data["customer_type"]
                .value_counts()
                .reset_index()
            )

            customer_counts.columns = [
                "Customer Type",
                "Bookings"
            ]

            fig_customer = px.bar(
                customer_counts,
                x="Bookings",
                y="Customer Type",
                orientation="h"
            )

            fig_customer.update_layout(
                margin=dict(
                    l=10,
                    r=10,
                    t=20,
                    b=10
                ),
                xaxis_title="Bookings",
                yaxis_title=""
            )

            st.plotly_chart(
                fig_customer,
                width="stretch"
            )

        else:

            st.info(
                "Customer type data is unavailable."
            )

    st.divider()

    # --------------------------------------------------------
    # AUTOMATIC EXECUTIVE INSIGHTS
    # --------------------------------------------------------

    st.markdown("### 📌 Executive Insights")

    insights = []

    # Hotel insight
    if "hotel" in data.columns:

        hotel_counts = data["hotel"].value_counts()

        if len(hotel_counts) > 0:

            top_hotel = hotel_counts.index[0]
            top_hotel_share = (
                hotel_counts.iloc[0]
                / total_bookings
                * 100
            )

            insights.append(
                f"🏨 **{top_hotel}** accounts for "
                f"approximately **{top_hotel_share:.1f}%** "
                f"of all bookings."
            )

    # Cancellation insight
    insights.append(
        f"❌ The overall cancellation rate is "
        f"**{cancellation_rate:.1f}%**, with "
        f"**{canceled_bookings:,}** bookings cancelled."
    )

    # ADR insight
    if "adr" in data.columns:

        highest_adr = data["adr"].max()

        insights.append(
            f"💰 The average daily rate (ADR) is "
            f"**{average_adr:,.2f}**, while the "
            f"maximum recorded ADR is "
            f"**{highest_adr:,.2f}**."
        )

    # Lead time insight
    if "lead_time" in data.columns:

        insights.append(
            f"⏳ Guests book an average of "
            f"**{average_lead_time:.1f} days** "
            f"in advance."
        )

    for insight in insights[:4]:

        st.info(insight)

    # --------------------------------------------------------
    # RECOMMENDATIONS
    # --------------------------------------------------------

    st.markdown("### 💡 Executive Recommendations")

    recommendations = []

    if cancellation_rate >= 30:

        recommendations.append(
            "❌ Cancellation risk is relatively high. "
            "Consider stronger cancellation policies, "
            "deposit requirements and booking reminders."
        )

    else:

        recommendations.append(
            "❌ Maintain current cancellation controls while "
            "monitoring high-risk booking segments."
        )

    if average_lead_time > 60:

        recommendations.append(
            "⏳ A high average lead time suggests an opportunity "
            "for early-booking incentives combined with "
            "appropriate cancellation policies."
        )

    else:

        recommendations.append(
            "⏳ Encourage advance bookings through early-bird "
            "offers to improve demand visibility."
        )

    recommendations.append(
        "💰 Use monthly demand and ADR patterns to support "
        "dynamic pricing during high- and low-demand periods."
    )

    recommendations.append(
        "🏨 Compare hotel-level cancellation and revenue "
        "performance regularly to allocate pricing and "
        "marketing efforts effectively."
    )

    for recommendation in recommendations[:4]:

        st.success(recommendation)

#===========================================================================================================================================================================================================
#page routing based on selected page
#===========================================================================================================================================================================================================

if selected_page == "📊 Executive Overview":
    render_executive_overview_page(prepared_df)