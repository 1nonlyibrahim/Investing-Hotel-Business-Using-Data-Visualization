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
import statsmodels.api as sm

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
        data["stay_duration"] = (
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
        data["stay_duration"] = 0

    # Estimated revenue
    if "adr" in data.columns:
        data["estimated_revenue"] = (
            pd.to_numeric(
                data["adr"],
                errors="coerce"
            ).fillna(0)
            *
            data["stay_duration"]
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
        "<h2 style='color: white; font-weight: bold;text-align: center;font-size: 40px; margin-bottom: 0.25rem;'>Executive Overview</h2>"
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
        data["stay_duration"].mean()
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
# HOTEL PERFORMANCE PAGE
#===========================================================================================================================================================================================================

def render_hotel_performance_page(df):

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
        data["stay_duration"] = (
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
        data["stay_duration"] = 0

    # Estimated revenue
    if "adr" in data.columns:

        data["estimated_revenue"] = (
            pd.to_numeric(
                data["adr"],
                errors="coerce"
            ).fillna(0)
            *
            data["stay_duration"]
        )

    else:

        data["estimated_revenue"] = 0

    # --------------------------------------------------------
    # PAGE HEADER / TEXT STYLE
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
        "<h2 style='color: white; font-weight: bold;text-align: center;font-size: 40px; margin-bottom: 0.25rem;'>Hotel Performance</h2>"
        "<p style='color: white; font-weight: normal; margin-top: 0;'>Comparison of City Hotel and Resort Hotel performance across bookings, pricing, cancellations and revenue.</p>",
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # CHECK HOTEL COLUMN
    # --------------------------------------------------------

    if "hotel" not in data.columns:

        st.warning(
            "⚠️ Hotel column is not available in the prepared dataset."
        )

        return

    # --------------------------------------------------------
    # BASIC HOTEL VALUES
    # --------------------------------------------------------

    hotel_counts = data["hotel"].value_counts()

    total_bookings = len(data)

    city_bookings = int(
        hotel_counts.get("City Hotel", 0)
    )

    resort_bookings = int(
        hotel_counts.get("Resort Hotel", 0)
    )

    city_share = (
        city_bookings / total_bookings * 100
        if total_bookings > 0
        else 0
    )

    resort_share = (
        resort_bookings / total_bookings * 100
        if total_bookings > 0
        else 0
    )

    # --------------------------------------------------------
    # CANCELLATION RATE
    # --------------------------------------------------------

    if "is_canceled" in data.columns:

        data["is_canceled"] = pd.to_numeric(
            data["is_canceled"],
            errors="coerce"
        ).fillna(0)

        city_cancel_rate = (
            data.loc[
                data["hotel"] == "City Hotel",
                "is_canceled"
            ].mean() * 100
            if city_bookings > 0
            else 0
        )

        resort_cancel_rate = (
            data.loc[
                data["hotel"] == "Resort Hotel",
                "is_canceled"
            ].mean() * 100
            if resort_bookings > 0
            else 0
        )

    else:

        city_cancel_rate = 0
        resort_cancel_rate = 0

    # --------------------------------------------------------
    # ADR
    # --------------------------------------------------------

    if "adr" in data.columns:

        data["adr"] = pd.to_numeric(
            data["adr"],
            errors="coerce"
        )

        city_adr = (
            data.loc[
                data["hotel"] == "City Hotel",
                "adr"
            ].mean()
            if city_bookings > 0
            else 0
        )

        resort_adr = (
            data.loc[
                data["hotel"] == "Resort Hotel",
                "adr"
            ].mean()
            if resort_bookings > 0
            else 0
        )

    else:

        city_adr = 0
        resort_adr = 0

    # --------------------------------------------------------
    # LEAD TIME
    # --------------------------------------------------------

    if "lead_time" in data.columns:

        data["lead_time"] = pd.to_numeric(
            data["lead_time"],
            errors="coerce"
        )

        city_lead_time = (
            data.loc[
                data["hotel"] == "City Hotel",
                "lead_time"
            ].mean()
            if city_bookings > 0
            else 0
        )

        resort_lead_time = (
            data.loc[
                data["hotel"] == "Resort Hotel",
                "lead_time"
            ].mean()
            if resort_bookings > 0
            else 0
        )

    else:

        city_lead_time = 0
        resort_lead_time = 0

    # --------------------------------------------------------
    # AVERAGE STAY
    # --------------------------------------------------------

    city_average_stay = (
        data.loc[
            data["hotel"] == "City Hotel",
            "stay_duration"
        ].mean()
        if city_bookings > 0
        else 0
    )

    resort_average_stay = (
        data.loc[
            data["hotel"] == "Resort Hotel",
            "stay_duration"
        ].mean()
        if resort_bookings > 0
        else 0
    )

    # --------------------------------------------------------
    # ESTIMATED REVENUE
    # --------------------------------------------------------

    city_revenue = (
        data.loc[
            data["hotel"] == "City Hotel",
            "estimated_revenue"
        ].sum()
    )

    resort_revenue = (
        data.loc[
            data["hotel"] == "Resort Hotel",
            "estimated_revenue"
        ].sum()
    )

    # --------------------------------------------------------
    # KPI SECTION
    # --------------------------------------------------------

    st.markdown(
        "<h3 style='color: white; font-weight: bold; margin-bottom: 0.5rem;'>📌 Hotel Performance KPIs</h3>",
        unsafe_allow_html=True
    )

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:

        st.metric(
            "City Hotel Bookings",
            f"{city_bookings:,}"
        )

    with kpi2:

        st.metric(
            "Resort Hotel Bookings",
            f"{resort_bookings:,}"
        )

    with kpi3:

        st.metric(
            "City Booking Share",
            f"{city_share:.1f}%"
        )

    with kpi4:

        st.metric(
            "Resort Booking Share",
            f"{resort_share:.1f}%"
        )

    kpi5, kpi6, kpi7, kpi8 = st.columns(4)

    with kpi5:

        st.metric(
            "City Cancellation Rate",
            f"{city_cancel_rate:.1f}%"
        )

    with kpi6:

        st.metric(
            "Resort Cancellation Rate",
            f"{resort_cancel_rate:.1f}%"
        )

    with kpi7:

        st.metric(
            "City Average ADR",
            f"{city_adr:,.2f}"
        )

    with kpi8:

        st.metric(
            "Resort Average ADR",
            f"{resort_adr:,.2f}"
        )

    st.divider()

    # --------------------------------------------------------
    # SECOND KPI ROW
    # --------------------------------------------------------

    kpi9, kpi10, kpi11, kpi12 = st.columns(4)

    with kpi9:

        st.metric(
            "City Average Lead Time",
            f"{city_lead_time:,.1f} days"
        )

    with kpi10:

        st.metric(
            "Resort Average Lead Time",
            f"{resort_lead_time:,.1f} days"
        )

    with kpi11:

        st.metric(
            "City Average Stay",
            f"{city_average_stay:,.1f} nights"
        )

    with kpi12:

        st.metric(
            "Resort Average Stay",
            f"{resort_average_stay:,.1f} nights"
        )

    # --------------------------------------------------------
    # REVENUE KPI
    # --------------------------------------------------------

    kpi13, kpi14 = st.columns(2)

    with kpi13:

        st.metric(
            "City Estimated Revenue",
            f"{city_revenue:,.0f}"
        )

    with kpi14:

        st.metric(
            "Resort Estimated Revenue",
            f"{resort_revenue:,.0f}"
        )

    st.divider()

    # ========================================================
    # ROW 1 — BOOKING DISTRIBUTION + ADR
    # ========================================================

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # HOTEL BOOKING DISTRIBUTION
    # --------------------------------------------------------

    with col1:

        st.markdown(
            "<h3 style='color: white; font-weight: bold;'>🏨 Hotel Booking Distribution</h3>",
            unsafe_allow_html=True
        )

        hotel_distribution = (
            data["hotel"]
            .value_counts()
            .reset_index()
        )

        hotel_distribution.columns = [
            "Hotel",
            "Bookings"
        ]

        fig_distribution = px.pie(
            hotel_distribution,
            names="Hotel",
            values="Bookings",
            hole=0.55
        )

        fig_distribution.update_layout(
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10
            ),
            legend_title=""
        )

        st.plotly_chart(
            fig_distribution,
            width="stretch"
        )

    # --------------------------------------------------------
    # ADR COMPARISON
    # --------------------------------------------------------

    with col2:

        st.markdown(
            "<h3 style='color: white; font-weight: bold;'>💰 ADR Comparison</h3>",
            unsafe_allow_html=True
        )

        adr_comparison = pd.DataFrame({
            "Hotel": [
                "City Hotel",
                "Resort Hotel"
            ],
            "Average ADR": [
                city_adr,
                resort_adr
            ]
        })

        fig_adr = px.bar(
            adr_comparison,
            x="Hotel",
            y="Average ADR",
            text="Average ADR"
        )

        fig_adr.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside"
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

    # ========================================================
    # ROW 2 — CANCELLATION + LEAD TIME
    # ========================================================

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # CANCELLATION RATE
    # --------------------------------------------------------

    with col1:

        st.markdown(
            "<h3 style='color: white; font-weight: bold;'>❌ Cancellation Rate Comparison</h3>",
            unsafe_allow_html=True
        )

        cancellation_comparison = pd.DataFrame({
            "Hotel": [
                "City Hotel",
                "Resort Hotel"
            ],
            "Cancellation Rate": [
                city_cancel_rate,
                resort_cancel_rate
            ]
        })

        fig_cancel = px.bar(
            cancellation_comparison,
            x="Hotel",
            y="Cancellation Rate",
            text="Cancellation Rate"
        )

        fig_cancel.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
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

    # --------------------------------------------------------
    # LEAD TIME COMPARISON
    # --------------------------------------------------------

    with col2:

        st.markdown(
            "<h3 style='color: white; font-weight: bold;'>⏳ Average Lead Time</h3>",
            unsafe_allow_html=True
        )

        lead_time_comparison = pd.DataFrame({
            "Hotel": [
                "City Hotel",
                "Resort Hotel"
            ],
            "Average Lead Time": [
                city_lead_time,
                resort_lead_time
            ]
        })

        fig_lead = px.bar(
            lead_time_comparison,
            x="Hotel",
            y="Average Lead Time",
            text="Average Lead Time"
        )

        fig_lead.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside"
        )

        fig_lead.update_layout(
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10
            ),
            xaxis_title="",
            yaxis_title="Days"
        )

        st.plotly_chart(
            fig_lead,
            width="stretch"
        )

    # ========================================================
    # ROW 3 — STAY + REVENUE
    # ========================================================

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # AVERAGE STAY
    # --------------------------------------------------------

    with col1:

        st.markdown(
            "<h3 style='color: white; font-weight: bold;'>🛏️ Average Stay Comparison</h3>",
            unsafe_allow_html=True
        )

        stay_comparison = pd.DataFrame({
            "Hotel": [
                "City Hotel",
                "Resort Hotel"
            ],
            "Average Stay": [
                city_average_stay,
                resort_average_stay
            ]
        })

        fig_stay = px.bar(
            stay_comparison,
            x="Hotel",
            y="Average Stay",
            text="Average Stay"
        )

        fig_stay.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside"
        )

        fig_stay.update_layout(
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10
            ),
            xaxis_title="",
            yaxis_title="Nights"
        )

        st.plotly_chart(
            fig_stay,
            width="stretch"
        )

    # --------------------------------------------------------
    # ESTIMATED REVENUE
    # --------------------------------------------------------

    with col2:

        st.markdown(
            "<h3 style='color: white; font-weight: bold;'>💵 Estimated Revenue</h3>",
            unsafe_allow_html=True
        )

        revenue_comparison = pd.DataFrame({
            "Hotel": [
                "City Hotel",
                "Resort Hotel"
            ],
            "Estimated Revenue": [
                city_revenue,
                resort_revenue
            ]
        })

        fig_revenue = px.bar(
            revenue_comparison,
            x="Hotel",
            y="Estimated Revenue",
            text="Estimated Revenue"
        )

        fig_revenue.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside"
        )

        fig_revenue.update_layout(
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10
            ),
            xaxis_title="",
            yaxis_title="Estimated Revenue"
        )

        st.plotly_chart(
            fig_revenue,
            width="stretch"
        )

    st.divider()

    # ========================================================
    # MONTHLY HOTEL PERFORMANCE
    # ========================================================

    st.markdown(
        "<h3 style='color: white; font-weight: bold;'>📅 Monthly Hotel Performance</h3>",
        unsafe_allow_html=True
    )

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

    if "arrival_date_month" in data.columns:

        monthly_hotel = (
            data.groupby(
                [
                    "arrival_date_month",
                    "hotel"
                ]
            )
            .size()
            .reset_index(
                name="Bookings"
            )
        )

        monthly_hotel[
            "arrival_date_month"
        ] = pd.Categorical(
            monthly_hotel[
                "arrival_date_month"
            ],
            categories=month_order,
            ordered=True
        )

        monthly_hotel = monthly_hotel.sort_values(
            "arrival_date_month"
        )

        fig_monthly = px.line(
            monthly_hotel,
            x="arrival_date_month",
            y="Bookings",
            color="hotel",
            markers=True
        )

        fig_monthly.update_layout(
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10
            ),
            xaxis_title="",
            yaxis_title="Bookings",
            legend_title="Hotel"
        )

        st.plotly_chart(
            fig_monthly,
            width="stretch"
        )

    else:

        st.info(
            "Arrival month column is not available."
        )

    st.divider()

    # ========================================================
    # HOTEL PERFORMANCE INSIGHTS
    # ========================================================

    st.markdown(
        "<h3 style='color: white; font-weight: bold;'>📌 Hotel Performance Insights</h3>",
        unsafe_allow_html=True
    )

    insights = []

    # Booking volume insight
    if city_bookings > resort_bookings:

        insights.append(
            f"🏨 **City Hotel** receives the larger booking volume "
            f"with **{city_bookings:,} bookings**, compared with "
            f"**{resort_bookings:,}** for Resort Hotel."
        )

    elif resort_bookings > city_bookings:

        insights.append(
            f"🏨 **Resort Hotel** receives the larger booking volume "
            f"with **{resort_bookings:,} bookings**, compared with "
            f"**{city_bookings:,}** for City Hotel."
        )

    # ADR insight
    if city_adr > resort_adr:

        insights.append(
            f"💰 **City Hotel** has the higher average ADR at "
            f"**{city_adr:,.2f}**, compared with "
            f"**{resort_adr:,.2f}** for Resort Hotel."
        )

    elif resort_adr > city_adr:

        insights.append(
            f"💰 **Resort Hotel** has the higher average ADR at "
            f"**{resort_adr:,.2f}**, compared with "
            f"**{city_adr:,.2f}** for City Hotel."
        )

    # Cancellation insight
    if city_cancel_rate > resort_cancel_rate:

        insights.append(
            f"❌ **City Hotel** has the higher cancellation rate "
            f"at **{city_cancel_rate:.1f}%**, indicating greater "
            f"cancellation exposure."
        )

    elif resort_cancel_rate > city_cancel_rate:

        insights.append(
            f"❌ **Resort Hotel** has the higher cancellation rate "
            f"at **{resort_cancel_rate:.1f}%**, indicating greater "
            f"cancellation exposure."
        )

    # Stay insight
    if city_average_stay > resort_average_stay:

        insights.append(
            f"🛏️ Guests stay longer at **City Hotel**, averaging "
            f"**{city_average_stay:.1f} nights** compared with "
            f"**{resort_average_stay:.1f} nights** at Resort Hotel."
        )

    elif resort_average_stay > city_average_stay:

        insights.append(
            f"🛏️ Guests stay longer at **Resort Hotel**, averaging "
            f"**{resort_average_stay:.1f} nights** compared with "
            f"**{city_average_stay:.1f} nights** at City Hotel."
        )

    # Revenue insight
    if city_revenue > resort_revenue:

        insights.append(
            f"💵 **City Hotel** generates the higher estimated revenue "
            f"of **{city_revenue:,.0f}**."
        )

    elif resort_revenue > city_revenue:

        insights.append(
            f"💵 **Resort Hotel** generates the higher estimated revenue "
            f"of **{resort_revenue:,.0f}**."
        )

    for insight in insights[:5]:

        st.info(insight)

    # ========================================================
    # HOTEL-SPECIFIC RECOMMENDATIONS
    # ========================================================

    st.markdown(
        "<h3 style='color: white; font-weight: bold;'>💡 Hotel-Specific Recommendations</h3>",
        unsafe_allow_html=True
    )

    recommendations = []

    # Cancellation recommendation
    if city_cancel_rate > resort_cancel_rate:

        recommendations.append(
            "❌ City Hotel should focus on reducing cancellation "
            "exposure through stronger cancellation policies, "
            "deposit requirements and booking reminders."
        )

    elif resort_cancel_rate > city_cancel_rate:

        recommendations.append(
            "❌ Resort Hotel should focus on reducing cancellation "
            "exposure through stronger cancellation policies, "
            "deposit requirements and booking reminders."
        )

    # ADR recommendation
    if city_adr > resort_adr:

        recommendations.append(
            "💰 Resort Hotel can evaluate premium pricing, "
            "package offerings and value-added services to "
            "improve its ADR."
        )

    elif resort_adr > city_adr:

        recommendations.append(
            "💰 City Hotel can evaluate premium pricing and "
            "value-added packages to improve its ADR."
        )

    # Stay recommendation
    if resort_average_stay > city_average_stay:

        recommendations.append(
            "🛏️ Resort Hotel can develop extended-stay and "
            "family packages to further encourage longer visits."
        )

    else:

        recommendations.append(
            "🛏️ City Hotel can explore extended-stay packages "
            "to increase average length of stay."
        )

    # General recommendation
    recommendations.append(
        "📊 Monitor hotel-level booking volume, ADR and "
        "cancellation rates regularly to optimize pricing, "
        "marketing and inventory decisions."
    )

    for recommendation in recommendations[:4]:

        st.success(recommendation)

#===========================================================================================================================================================================================================
# BOOKING TRENDS PAGE
#===========================================================================================================================================================================================================

def render_booking_trends_page(df):

    if df is None or df.empty:
        st.info("📂 Please upload and prepare your dataset first.")
        return

    # --------------------------------------------------------
    # WORKING COPY
    # --------------------------------------------------------

    data = df.copy()

    # --------------------------------------------------------
    # PAGE STYLE
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

    # --------------------------------------------------------
    # PAGE HEADER
    # --------------------------------------------------------

    st.markdown(
        "<h2 style='color: white; font-weight: bold; text-align: center; font-size: 40px; margin-bottom: 0.25rem;'>Booking Trends</h2>"
        "<p style='color: white; font-weight: normal; margin-top: 0;'>Analysis of booking demand, arrival patterns, seasonality, cancellations and pricing trends.</p>",
        unsafe_allow_html=True
    )

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
    # REQUIRED COLUMNS CHECK
    # --------------------------------------------------------

    if "arrival_date_month" not in data.columns:

        st.warning(
            "⚠️ Arrival month information is not available in the prepared dataset."
        )

        return

    # --------------------------------------------------------
    # CLEAN MONTH COLUMN
    # --------------------------------------------------------

    data["arrival_date_month"] = pd.Categorical(
        data["arrival_date_month"],
        categories=month_order,
        ordered=True
    )

    # ========================================================
    # PREPARE BOOKING DATA
    # ========================================================

    monthly_bookings = (
        data.groupby(
            "arrival_date_month",
            observed=True
        )
        .size()
        .reset_index(
            name="Bookings"
        )
    )

    # --------------------------------------------------------
    # PEAK / LOW MONTH
    # --------------------------------------------------------

    if not monthly_bookings.empty:

        peak_month_row = monthly_bookings.loc[
            monthly_bookings["Bookings"].idxmax()
        ]

        lowest_month_row = monthly_bookings.loc[
            monthly_bookings["Bookings"].idxmin()
        ]

        peak_booking_month = peak_month_row["arrival_date_month"]

        lowest_booking_month = lowest_month_row["arrival_date_month"]

        peak_booking_count = int(
            peak_month_row["Bookings"]
        )

        lowest_booking_count = int(
            lowest_month_row["Bookings"]
        )

        average_monthly_bookings = (
            monthly_bookings["Bookings"].mean()
        )

    else:

        peak_booking_month = "N/A"
        lowest_booking_month = "N/A"
        peak_booking_count = 0
        lowest_booking_count = 0
        average_monthly_bookings = 0

    # ========================================================
    # PEAK ARRIVAL MONTH
    # ========================================================

    peak_arrival_month = peak_booking_month

    # ========================================================
    # PEAK SEASON
    # ========================================================

    season_mapping = {
        "December": "Winter",
        "January": "Winter",
        "February": "Winter",
        "March": "Spring",
        "April": "Spring",
        "May": "Spring",
        "June": "Summer",
        "July": "Summer",
        "August": "Summer",
        "September": "Autumn",
        "October": "Autumn",
        "November": "Autumn"
    }

    season_data = data.copy()

    season_data["Season"] = (
        season_data["arrival_date_month"]
        .astype(str)
        .map(season_mapping)
    )

    seasonal_bookings = (
        season_data["Season"]
        .value_counts()
    )

    if not seasonal_bookings.empty:

        peak_season = seasonal_bookings.idxmax()

    else:

        peak_season = "N/A"

    # ========================================================
    # KPI SECTION
    # ========================================================

    st.markdown(
        "<h3 style='color: white; font-weight: bold; margin-bottom: 0.5rem;'>📌 Booking Trend KPIs</h3>",
        unsafe_allow_html=True
    )

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    with kpi1:

        st.metric(
            "Peak Booking Month",
            str(peak_booking_month)
        )

    with kpi2:

        st.metric(
            "Lowest Booking Month",
            str(lowest_booking_month)
        )

    with kpi3:

        st.metric(
            "Peak Arrival Month",
            str(peak_arrival_month)
        )

    with kpi4:

        st.metric(
            "Avg Monthly Bookings",
            f"{average_monthly_bookings:,.0f}"
        )

    with kpi5:

        st.metric(
            "Peak Booking Season",
            str(peak_season)
        )

    st.divider()

    # ========================================================
    # ROW 1 — MONTHLY BOOKINGS + HOTEL BOOKINGS
    # ========================================================

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # MONTHLY BOOKINGS
    # --------------------------------------------------------

    with col1:

        st.markdown(
            "<h3 style='color: white; font-weight: bold;'>📅 Monthly Bookings</h3>",
            unsafe_allow_html=True
        )

        fig_monthly_bookings = px.line(
            monthly_bookings,
            x="arrival_date_month",
            y="Bookings",
            markers=True
        )

        fig_monthly_bookings.update_layout(
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
            fig_monthly_bookings,
            width="stretch"
        )

    # --------------------------------------------------------
    # MONTHLY BOOKINGS BY HOTEL
    # --------------------------------------------------------

    with col2:

        st.markdown(
            "<h3 style='color: white; font-weight: bold;'>🏨 Monthly Bookings by Hotel</h3>",
            unsafe_allow_html=True
        )

        if "hotel" in data.columns:

            monthly_hotel = (
                data.groupby(
                    [
                        "arrival_date_month",
                        "hotel"
                    ],
                    observed=True
                )
                .size()
                .reset_index(
                    name="Bookings"
                )
            )

            fig_hotel = px.line(
                monthly_hotel,
                x="arrival_date_month",
                y="Bookings",
                color="hotel",
                markers=True
            )

            fig_hotel.update_layout(
                margin=dict(
                    l=10,
                    r=10,
                    t=20,
                    b=10
                ),
                xaxis_title="",
                yaxis_title="Bookings",
                legend_title="Hotel"
            )

            st.plotly_chart(
                fig_hotel,
                width="stretch"
            )

        else:

            st.info(
                "Hotel information is not available."
            )

    # ========================================================
    # ROW 2 — CANCELLATION + ADR
    # ========================================================

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # MONTHLY CANCELLATION RATE
    # --------------------------------------------------------

    with col1:

        st.markdown(
            "<h3 style='color: white; font-weight: bold;'>❌ Monthly Cancellation Rate</h3>",
            unsafe_allow_html=True
        )

        if "is_canceled" in data.columns:

            data["is_canceled"] = pd.to_numeric(
                data["is_canceled"],
                errors="coerce"
            ).fillna(0)

            monthly_cancellation = (
                data.groupby(
                    "arrival_date_month",
                    observed=True
                )["is_canceled"]
                .mean()
                .reset_index()
            )

            monthly_cancellation["Cancellation Rate"] = (
                monthly_cancellation["is_canceled"] * 100
            )

            fig_cancellation = px.line(
                monthly_cancellation,
                x="arrival_date_month",
                y="Cancellation Rate",
                markers=True
            )

            fig_cancellation.update_layout(
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
                fig_cancellation,
                width="stretch"
            )

        else:

            st.info(
                "Cancellation information is not available."
            )

    # --------------------------------------------------------
    # MONTHLY ADR
    # --------------------------------------------------------

    with col2:

        st.markdown(
            "<h3 style='color: white; font-weight: bold;'>💰 Monthly ADR</h3>",
            unsafe_allow_html=True
        )

        if "adr" in data.columns:

            data["adr"] = pd.to_numeric(
                data["adr"],
                errors="coerce"
            )

            monthly_adr = (
                data.groupby(
                    "arrival_date_month",
                    observed=True
                )["adr"]
                .mean()
                .reset_index()
            )

            fig_adr = px.line(
                monthly_adr,
                x="arrival_date_month",
                y="adr",
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
                "ADR information is not available."
            )

    # ========================================================
    # ROW 3 — MONTHLY REVENUE + ARRIVAL DAY
    # ========================================================

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # MONTHLY REVENUE
    # --------------------------------------------------------
    if all(col in prepared_df.columns for col in [
                "adr",
                "stays_in_weekend_nights",
                "stays_in_week_nights"
            ]):

                prepared_df["adr"] = pd.to_numeric(
                    prepared_df["adr"],
                    errors="coerce"
                ).fillna(0)

                prepared_df["stays_in_weekend_nights"] = pd.to_numeric(
                    prepared_df["stays_in_weekend_nights"],
                    errors="coerce"
                ).fillna(0)

                prepared_df["stays_in_week_nights"] = pd.to_numeric(
                    prepared_df["stays_in_week_nights"],
                    errors="coerce"
                ).fillna(0)

                prepared_df["stay_duration"] = (
                    prepared_df["stays_in_weekend_nights"]
                    + prepared_df["stays_in_week_nights"]
                )

                prepared_df["estimated_revenue"] = (
                    prepared_df["adr"]
                    * prepared_df["stay_duration"]
                )
    with col1:
        # Create Estimated Revenue
        st.markdown(
            "<h3 style='color: white; font-weight: bold;'>💵 Monthly Estimated Revenue</h3>",
            unsafe_allow_html=True
        )

        if (
            "adr" in data.columns
            and
            "stays_in_weekend_nights" in data.columns
            and
            "stays_in_week_nights" in data.columns
        ):

            data["stays_in_weekend_nights"] = pd.to_numeric(
                data["stays_in_weekend_nights"],
                errors="coerce"
            ).fillna(0)

            data["stays_in_week_nights"] = pd.to_numeric(
                data["stays_in_week_nights"],
                errors="coerce"
            ).fillna(0)

            data["estimated_revenue"] = (
                data["adr"].fillna(0)
                *
                (
                    data["stays_in_weekend_nights"]
                    +
                    data["stays_in_week_nights"]
                )
            )

            monthly_revenue = (
                data.groupby(
                    "arrival_date_month",
                    observed=True
                )["estimated_revenue"]
                .sum()
                .reset_index()
            )

            fig_revenue = px.line(
                monthly_revenue,
                x="arrival_date_month",
                y="estimated_revenue",
                markers=True
            )

            fig_revenue.update_layout(
                margin=dict(
                    l=10,
                    r=10,
                    t=20,
                    b=10
                ),
                xaxis_title="",
                yaxis_title="Estimated Revenue"
            )

            st.plotly_chart(
                fig_revenue,
                width="stretch"
            )

        else:

            st.info(
                "Required revenue columns are not available."
            )

    # --------------------------------------------------------
    # BOOKINGS BY ARRIVAL DAY
    # --------------------------------------------------------

    with col2:

        st.markdown(
            "<h3 style='color: white; font-weight: bold;'>📆 Bookings by Arrival Day</h3>",
            unsafe_allow_html=True
        )

        if "arrival_date_day_of_month" in data.columns:

            arrival_day = (
                data["arrival_date_day_of_month"]
                .value_counts()
                .sort_index()
                .reset_index()
            )

            arrival_day.columns = [
                "Arrival Day",
                "Bookings"
            ]

            fig_arrival_day = px.bar(
                arrival_day,
                x="Arrival Day",
                y="Bookings"
            )

            fig_arrival_day.update_layout(
                margin=dict(
                    l=10,
                    r=10,
                    t=20,
                    b=10
                ),
                xaxis_title="Day of Month",
                yaxis_title="Bookings"
            )

            st.plotly_chart(
                fig_arrival_day,
                width="stretch"
            )

        else:

            st.info(
                "Arrival day information is not available."
            )

    # ========================================================
    # WEEK NUMBER ANALYSIS
    # ========================================================

    st.markdown(
        "<h3 style='color: white; font-weight: bold;'>📊 Bookings by Week Number</h3>",
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # CREATE WEEK NUMBER
    # --------------------------------------------------------

    if "arrival_date_week_number" in data.columns:

        weekly_bookings = (
            data.groupby(
                "arrival_date_week_number"
            )
            .size()
            .reset_index(
                name="Bookings"
            )
            .sort_values(
                "arrival_date_week_number"
            )
        )

        fig_week = px.line(
            weekly_bookings,
            x="arrival_date_week_number",
            y="Bookings",
            markers=True
        )

        fig_week.update_layout(
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10
            ),
            xaxis_title="Week Number",
            yaxis_title="Bookings"
        )

        st.plotly_chart(
            fig_week,
            width="stretch"
        )

    else:

        st.info(
            "Arrival week number information is not available."
        )

    st.divider()

    # ========================================================
    # SEASONALITY ANALYSIS
    # ========================================================

    st.markdown(
        "<h3 style='color: white; font-weight: bold;'>🌦️ Seasonal Demand</h3>",
        unsafe_allow_html=True
    )

    seasonal_chart = (
        season_data.groupby(
            "Season"
        )
        .size()
        .reset_index(
            name="Bookings"
        )
    )

    season_order = [
        "Winter",
        "Spring",
        "Summer",
        "Autumn"
    ]

    seasonal_chart["Season"] = pd.Categorical(
        seasonal_chart["Season"],
        categories=season_order,
        ordered=True
    )

    seasonal_chart = seasonal_chart.sort_values(
        "Season"
    )

    fig_season = px.bar(
        seasonal_chart,
        x="Season",
        y="Bookings",
        text="Bookings"
    )

    fig_season.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig_season.update_layout(
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
        fig_season,
        width="stretch"
    )

    st.divider()

    # ========================================================
    # BOOKING TREND INSIGHTS
    # ========================================================

    st.markdown(
        "<h3 style='color: white; font-weight: bold;'>📌 Booking Trend Insights</h3>",
        unsafe_allow_html=True
    )

    insights = []

    # Peak month
    if peak_booking_month != "N/A":

        insights.append(
            f"📈 **{peak_booking_month}** records the highest "
            f"booking demand with **{peak_booking_count:,} bookings**."
        )

    # Lowest month
    if lowest_booking_month != "N/A":

        insights.append(
            f"📉 **{lowest_booking_month}** has the lowest booking "
            f"demand with **{lowest_booking_count:,} bookings**."
        )

    # Seasonal insight
    if peak_season != "N/A":

        insights.append(
            f"🌦️ **{peak_season}** is the strongest booking season "
            f"based on total arrival demand."
        )

    # Cancellation insight
    if (
        "is_canceled" in data.columns
        and "arrival_date_month" in data.columns
    ):

        highest_cancel_row = monthly_cancellation.loc[
            monthly_cancellation["Cancellation Rate"].idxmax()
        ]

        highest_cancel_month = (
            highest_cancel_row["arrival_date_month"]
        )

        highest_cancel_rate = (
            highest_cancel_row["Cancellation Rate"]
        )

        insights.append(
            f"❌ **{highest_cancel_month}** has the highest monthly "
            f"cancellation rate at **{highest_cancel_rate:.1f}%**."
        )

    # ADR insight
    if "adr" in data.columns:

        highest_adr_row = monthly_adr.loc[
            monthly_adr["adr"].idxmax()
        ]

        highest_adr_month = (
            highest_adr_row["arrival_date_month"]
        )

        highest_adr_value = (
            highest_adr_row["adr"]
        )

        insights.append(
            f"💰 Average ADR reaches its highest level in "
            f"**{highest_adr_month}** at **{highest_adr_value:,.2f}**."
        )

    for insight in insights[:5]:

        st.info(insight)

    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    st.markdown(
        "<h3 style='color: white; font-weight: bold;'>💡 Booking Trend Recommendations</h3>",
        unsafe_allow_html=True
    )

    recommendations = []

    # Peak season recommendation
    if peak_booking_month != "N/A":

        recommendations.append(
            f"📈 Increase room availability, pricing flexibility "
            f"and inventory planning around peak demand periods "
            f"such as **{peak_booking_month}**."
        )

    # Low season recommendation
    if lowest_booking_month != "N/A":

        recommendations.append(
            f"📉 Use targeted promotions, packages and discounts "
            f"during weaker demand periods such as "
            f"**{lowest_booking_month}**."
        )

    # Cancellation recommendation
    if (
        "is_canceled" in data.columns
        and not monthly_cancellation.empty
    ):

        recommendations.append(
            "❌ Monitor months with unusually high cancellation "
            "rates and consider stronger cancellation policies "
            "or deposit requirements during those periods."
        )

    # Pricing recommendation
    if "adr" in data.columns:

        recommendations.append(
            "💰 Adjust ADR according to seasonal demand by "
            "increasing prices during strong demand periods "
            "and using promotional pricing during weaker periods."
        )

    for recommendation in recommendations[:4]:

        st.success(recommendation)

# =================================================================================================
# ❌ CANCELLATION ANALYSIS PAGE
# =================================================================================================

def render_cancellation_analysis_page(df):

    if df is None or df.empty:
        st.info("📂 Please upload and prepare your dataset first.")
        return

    data = df.copy()

    # =============================================================================================
    # PAGE HEADER
    # =============================================================================================

    st.markdown(
        """
        <h2 style="
            color: white;
            font-weight: bold;
            text-align: center;
            font-size: 40px;
            margin-bottom: 0.25rem;
        ">
            ❌ Cancellation Analysis
        </h2>

        <p style="
            color: white;
            margin-top: 0;
        ">
            Identify cancellation patterns, risk factors and the strongest drivers
            of booking cancellations.
        </p>
        """,
        unsafe_allow_html=True
    )

    # =============================================================================================
    # REQUIRED COLUMN CHECK
    # =============================================================================================

    if "is_canceled" not in data.columns:

        st.error(
            "❌ The required column 'is_canceled' is not available in the prepared dataset."
        )
        return

    # =============================================================================================
    # BASIC DATA PREPARATION
    # =============================================================================================

    data["is_canceled"] = pd.to_numeric(
        data["is_canceled"],
        errors="coerce"
    ).fillna(0)

    data["is_canceled"] = data["is_canceled"].astype(int)

    # =============================================================================================
    # TOTAL BOOKINGS
    # =============================================================================================

    total_bookings = len(data)

    cancelled_bookings = int(
        data["is_canceled"].sum()
    )

    confirmed_bookings = (
        total_bookings - cancelled_bookings
    )

    cancellation_rate = (
        cancelled_bookings / total_bookings * 100
        if total_bookings > 0
        else 0
    )

    # =============================================================================================
    # CANCELLED BOOKING DATA
    # =============================================================================================

    cancelled_data = data[
        data["is_canceled"] == 1
    ].copy()

    # =============================================================================================
    # AVERAGE LEAD TIME OF CANCELLED BOOKINGS
    # =============================================================================================

    if "lead_time" in data.columns:

        data["lead_time"] = pd.to_numeric(
            data["lead_time"],
            errors="coerce"
        )

        avg_cancelled_lead_time = (
            cancelled_data["lead_time"].mean()
            if not cancelled_data.empty
            else 0
        )

    else:

        avg_cancelled_lead_time = 0

    # =============================================================================================
    # ESTIMATED REVENUE
    # =============================================================================================

    if all(
        col in data.columns
        for col in [
            "adr",
            "stays_in_weekend_nights",
            "stays_in_week_nights"
        ]
    ):

        data["adr"] = pd.to_numeric(
            data["adr"],
            errors="coerce"
        ).fillna(0)

        data["stays_in_weekend_nights"] = pd.to_numeric(
            data["stays_in_weekend_nights"],
            errors="coerce"
        ).fillna(0)

        data["stays_in_week_nights"] = pd.to_numeric(
            data["stays_in_week_nights"],
            errors="coerce"
        ).fillna(0)

        data["stay_duration"] = (
            data["stays_in_weekend_nights"]
            +
            data["stays_in_week_nights"]
        )

        data["estimated_revenue"] = (
            data["adr"]
            *
            data["stay_duration"]
        )

        revenue_lost = (
            data.loc[
                data["is_canceled"] == 1,
                "estimated_revenue"
            ].sum()
        )

    else:

        revenue_lost = 0

    # =============================================================================================
    # KPI SECTION
    # =============================================================================================

    st.markdown(
        """
        <h3 style="color: white; font-weight: bold;">
            📌 Cancellation KPIs
        </h3>
        """,
        unsafe_allow_html=True
    )

    kpi1, kpi2, kpi3 = st.columns(3)

    kpi4, kpi5, kpi6 = st.columns(3)

    with kpi1:

        st.metric(
            "Total Bookings",
            f"{total_bookings:,}"
        )

    with kpi2:

        st.metric(
            "Cancelled Bookings",
            f"{cancelled_bookings:,}"
        )

    with kpi3:

        st.metric(
            "Confirmed Bookings",
            f"{confirmed_bookings:,}"
        )

    with kpi4:

        st.metric(
            "Cancellation Rate",
            f"{cancellation_rate:.2f}%"
        )

    with kpi5:

        st.metric(
            "Estimated Revenue Lost",
            f"{revenue_lost:,.2f}"
        )

    with kpi6:

        st.metric(
            "Avg Lead Time of Cancelled",
            f"{avg_cancelled_lead_time:.1f} days"
        )

    st.divider()

    # =============================================================================================
    # CANCELLATION BY HOTEL
    # =============================================================================================

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "### 🏨 Cancellation by Hotel"
        )

        if "hotel" in data.columns:

            hotel_cancel = (
                data.groupby("hotel")["is_canceled"]
                .mean()
                .reset_index()
            )

            hotel_cancel["Cancellation Rate"] = (
                hotel_cancel["is_canceled"] * 100
            )

            fig = px.bar(
                hotel_cancel,
                x="hotel",
                y="Cancellation Rate",
                text="Cancellation Rate"
            )

            fig.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside"
            )

            fig.update_layout(
                xaxis_title="Hotel",
                yaxis_title="Cancellation Rate (%)"
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.info("Hotel column is not available.")

    # =============================================================================================
    # CANCELLATION BY MONTH
    # =============================================================================================

    with col2:

        st.markdown(
            "### 📅 Cancellation by Month"
        )

        if "arrival_date_month" in data.columns:

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

            data["arrival_date_month"] = pd.Categorical(
                data["arrival_date_month"],
                categories=month_order,
                ordered=True
            )

            monthly_cancel = (
                data.groupby(
                    "arrival_date_month",
                    observed=True
                )["is_canceled"]
                .mean()
                .reset_index()
            )

            monthly_cancel["Cancellation Rate"] = (
                monthly_cancel["is_canceled"] * 100
            )

            fig = px.line(
                monthly_cancel,
                x="arrival_date_month",
                y="Cancellation Rate",
                markers=True
            )

            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Cancellation Rate (%)"
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.info(
                "Arrival month column is not available."
            )

    # =============================================================================================
    # MARKET SEGMENT
    # =============================================================================================

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "### 📢 Cancellation by Market Segment"
        )

        if "market_segment" in data.columns:

            segment_cancel = (
                data.groupby("market_segment")["is_canceled"]
                .mean()
                .reset_index()
            )

            segment_cancel["Cancellation Rate"] = (
                segment_cancel["is_canceled"] * 100
            )

            fig = px.bar(
                segment_cancel,
                x="market_segment",
                y="Cancellation Rate",
                text="Cancellation Rate"
            )

            fig.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside"
            )

            fig.update_layout(
                xaxis_title="Market Segment",
                yaxis_title="Cancellation Rate (%)"
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.info(
                "Market segment column is not available."
            )

    # =============================================================================================
    # DISTRIBUTION CHANNEL
    # =============================================================================================

    with col2:

        st.markdown(
            "### 📡 Cancellation by Distribution Channel"
        )

        if "distribution_channel" in data.columns:

            channel_cancel = (
                data.groupby(
                    "distribution_channel"
                )["is_canceled"]
                .mean()
                .reset_index()
            )

            channel_cancel["Cancellation Rate"] = (
                channel_cancel["is_canceled"] * 100
            )

            fig = px.bar(
                channel_cancel,
                x="distribution_channel",
                y="Cancellation Rate",
                text="Cancellation Rate"
            )

            fig.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside"
            )

            fig.update_layout(
                xaxis_title="Distribution Channel",
                yaxis_title="Cancellation Rate (%)"
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.info(
                "Distribution channel column is not available."
            )

    # =============================================================================================
    # DEPOSIT TYPE
    # =============================================================================================

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "### 💳 Cancellation by Deposit Type"
        )

        if "deposit_type" in data.columns:

            deposit_cancel = (
                data.groupby(
                    "deposit_type"
                )["is_canceled"]
                .mean()
                .reset_index()
            )

            deposit_cancel["Cancellation Rate"] = (
                deposit_cancel["is_canceled"] * 100
            )

            fig = px.bar(
                deposit_cancel,
                x="deposit_type",
                y="Cancellation Rate",
                text="Cancellation Rate"
            )

            fig.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside"
            )

            fig.update_layout(
                xaxis_title="Deposit Type",
                yaxis_title="Cancellation Rate (%)"
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.info(
                "Deposit type column is not available."
            )

    # =============================================================================================
    # CUSTOMER TYPE
    # =============================================================================================

    with col2:

        st.markdown(
            "### 👥 Cancellation by Customer Type"
        )

        if "customer_type" in data.columns:

            customer_cancel = (
                data.groupby(
                    "customer_type"
                )["is_canceled"]
                .mean()
                .reset_index()
            )

            customer_cancel["Cancellation Rate"] = (
                customer_cancel["is_canceled"] * 100
            )

            fig = px.bar(
                customer_cancel,
                x="customer_type",
                y="Cancellation Rate",
                text="Cancellation Rate"
            )

            fig.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside"
            )

            fig.update_layout(
                xaxis_title="Customer Type",
                yaxis_title="Cancellation Rate (%)"
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.info(
                "Customer type column is not available."
            )

    # =============================================================================================
    # REPEAT GUEST
    # =============================================================================================

    st.markdown(
        "### 🔁 Cancellation by Repeat Guest"
    )

    if "is_repeated_guest" in data.columns:

        repeat_cancel = (
            data.groupby(
                "is_repeated_guest"
            )["is_canceled"]
            .mean()
            .reset_index()
        )

        repeat_cancel["Guest Type"] = (
            repeat_cancel["is_repeated_guest"]
            .map({
                0: "New Guest",
                1: "Repeat Guest"
            })
        )

        repeat_cancel["Cancellation Rate"] = (
            repeat_cancel["is_canceled"] * 100
        )

        fig = px.bar(
            repeat_cancel,
            x="Guest Type",
            y="Cancellation Rate",
            text="Cancellation Rate"
        )

        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )

        fig.update_layout(
            xaxis_title="Guest Type",
            yaxis_title="Cancellation Rate (%)"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    else:

        st.info(
            "Repeat guest information is not available."
        )

    # =============================================================================================
    # LEAD TIME GROUP
    # =============================================================================================

    st.markdown(
        "### ⏳ Cancellation by Lead-Time Group"
    )

    if "lead_time" in data.columns:

        data["Lead Time Group"] = pd.cut(
            data["lead_time"],
            bins=[
                -1,
                30,
                60,
                90,
                180,
                float("inf")
            ],
            labels=[
                "0–30 days",
                "31–60 days",
                "61–90 days",
                "91–180 days",
                "180+ days"
            ]
        )

        lead_cancel = (
            data.groupby(
                "Lead Time Group",
                observed=True
            )
            .agg(
                Bookings=("is_canceled", "size"),
                Cancellation_Rate=("is_canceled", "mean")
            )
            .reset_index()
        )

        lead_cancel["Cancellation Rate"] = (
            lead_cancel["Cancellation_Rate"] * 100
        )

        fig = px.bar(
            lead_cancel,
            x="Lead Time Group",
            y="Cancellation Rate",
            text="Cancellation Rate"
        )

        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )

        fig.update_layout(
            xaxis_title="Lead-Time Group",
            yaxis_title="Cancellation Rate (%)"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    else:

        st.info(
            "Lead time information is not available."
        )

    # =============================================================================================
    # STAY DURATION GROUP
    # =============================================================================================

    st.markdown(
        "### 🛏️ Cancellation by Stay Duration"
    )

    if all(
        col in data.columns
        for col in [
            "stays_in_weekend_nights",
            "stays_in_week_nights"
        ]
    ):

        data["stay_duration"] = (
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

        data["Stay Group"] = pd.cut(
            data["stay_duration"],
            bins=[
                0,
                1,
                3,
                7,
                14,
                float("inf")
            ],
            labels=[
                "1 night",
                "2–3 nights",
                "4–7 nights",
                "8–14 nights",
                "15+ nights"
            ]
        )

        stay_cancel = (
            data.groupby(
                "Stay Group",
                observed=True
            )["is_canceled"]
            .mean()
            .reset_index()
        )

        stay_cancel["Cancellation Rate"] = (
            stay_cancel["is_canceled"] * 100
        )

        fig = px.bar(
            stay_cancel,
            x="Stay Group",
            y="Cancellation Rate",
            text="Cancellation Rate"
        )

        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )

        fig.update_layout(
            xaxis_title="Stay Duration",
            yaxis_title="Cancellation Rate (%)"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    else:

        st.info(
            "Stay duration columns are not available."
        )

    # =============================================================================================
    # KEY INSIGHTS
    # =============================================================================================

    st.divider()

    st.markdown(
        "### 📌 Key Cancellation Insights"
    )

    insights = []

    # Hotel insight
    if "hotel" in data.columns:

        hotel_rates = (
            data.groupby("hotel")["is_canceled"]
            .mean()
            .mul(100)
        )

        highest_hotel = hotel_rates.idxmax()
        highest_hotel_rate = hotel_rates.max()

        insights.append(
            f"🏨 **{highest_hotel}** has the highest cancellation rate "
            f"at **{highest_hotel_rate:.1f}%**."
        )

    # Market insight
    if "market_segment" in data.columns:

        segment_rates = (
            data.groupby("market_segment")["is_canceled"]
            .mean()
            .mul(100)
        )

        highest_segment = segment_rates.idxmax()
        highest_segment_rate = segment_rates.max()

        insights.append(
            f"📢 **{highest_segment}** has the highest cancellation "
            f"rate among market segments at **{highest_segment_rate:.1f}%**."
        )

    # Lead-time insight
    if "Lead Time Group" in data.columns:

        lead_rates = (
            data.groupby(
                "Lead Time Group",
                observed=True
            )["is_canceled"]
            .mean()
            .mul(100)
        )

        if not lead_rates.empty:

            highest_lead_group = lead_rates.idxmax()
            highest_lead_rate = lead_rates.max()

            insights.append(
                f"⏳ The **{highest_lead_group}** booking group "
                f"shows the highest cancellation rate at "
                f"**{highest_lead_rate:.1f}%**."
            )

    # Deposit insight
    if "deposit_type" in data.columns:

        deposit_rates = (
            data.groupby("deposit_type")["is_canceled"]
            .mean()
            .mul(100)
        )

        highest_deposit = deposit_rates.idxmax()

        insights.append(
            f"💳 **{highest_deposit}** deposit bookings show the "
            f"highest cancellation exposure."
        )

    # Repeat guest insight
    if "is_repeated_guest" in data.columns:

        repeat_rates = (
            data.groupby(
                "is_repeated_guest"
            )["is_canceled"]
            .mean()
            .mul(100)
        )

        if 0 in repeat_rates.index and 1 in repeat_rates.index:

            new_rate = repeat_rates.loc[0]
            repeat_rate = repeat_rates.loc[1]

            if repeat_rate < new_rate:

                insights.append(
                    f"🔁 Repeat guests have a lower cancellation "
                    f"rate (**{repeat_rate:.1f}%**) compared with "
                    f"new guests (**{new_rate:.1f}%**)."
                )

            else:

                insights.append(
                    f"🔁 Repeat guests have a higher cancellation "
                    f"rate (**{repeat_rate:.1f}%**) compared with "
                    f"new guests (**{new_rate:.1f}%**)."
                )

    for insight in insights[:5]:

        st.info(insight)

    # =============================================================================================
    # RECOMMENDATIONS
    # =============================================================================================

    st.markdown(
        "### 💡 Cancellation Recommendations"
    )

    recommendations = [
        "🎯 Identify high-risk booking segments and apply stronger cancellation or deposit policies where appropriate.",
        "📧 Send automated reminders before the cancellation deadline to reduce avoidable cancellations.",
        "💳 Review deposit policies for booking categories with unusually high cancellation rates.",
        "📊 Monitor long-lead-time bookings closely because advance bookings can create greater cancellation exposure.",
        "🔁 Encourage repeat bookings and loyalty programs if repeat guests demonstrate lower cancellation rates."
    ]

    for recommendation in recommendations:

        st.success(
            recommendation
        )

# =================================================================================================
# ⏳ LEAD TIME ANALYSIS PAGE
# =================================================================================================

def render_lead_time_analysis_page(df):

    if df is None or df.empty:
        st.info("📂 Please upload and prepare your dataset first.")
        return

    data = df.copy()

    # =============================================================================================
    # PAGE HEADER
    # =============================================================================================

    st.markdown(
        """
        <h2 style="
            color: white;
            font-weight: bold;
            text-align: center;
            font-size: 40px;
            margin-bottom: 0.25rem;
        ">
            ⏳ Lead Time Analysis
        </h2>

        <p style="
            color: white;
            margin-top: 0;
        ">
            Analyze how far in advance customers book their stays and whether
            longer lead times are associated with higher cancellation risk.
        </p>
        """,
        unsafe_allow_html=True
    )

    # =============================================================================================
    # REQUIRED COLUMN
    # =============================================================================================

    if "lead_time" not in data.columns:
        st.error(
            "❌ The required column 'lead_time' is not available in the prepared dataset."
        )
        return

    # =============================================================================================
    # DATA PREPARATION
    # =============================================================================================

    data["lead_time"] = pd.to_numeric(
        data["lead_time"],
        errors="coerce"
    )

    data = data.dropna(
        subset=["lead_time"]
    ).copy()

    data["lead_time"] = data["lead_time"].clip(lower=0)

    # =============================================================================================
    # CANCELLATION COLUMN
    # =============================================================================================

    if "is_canceled" in data.columns:

        data["is_canceled"] = pd.to_numeric(
            data["is_canceled"],
            errors="coerce"
        ).fillna(0)

        data["is_canceled"] = data["is_canceled"].astype(int)

    else:

        data["is_canceled"] = 0

    # =============================================================================================
    # ADR
    # =============================================================================================

    if "adr" in data.columns:

        data["adr"] = pd.to_numeric(
            data["adr"],
            errors="coerce"
        )

    # =============================================================================================
    # STAY NIGHTS
    # =============================================================================================

    if all(
        col in data.columns
        for col in [
            "stays_in_weekend_nights",
            "stays_in_week_nights"
        ]
    ):

        data["stays_in_weekend_nights"] = pd.to_numeric(
            data["stays_in_weekend_nights"],
            errors="coerce"
        ).fillna(0)

        data["stays_in_week_nights"] = pd.to_numeric(
            data["stays_in_week_nights"],
            errors="coerce"
        ).fillna(0)

        data["stay_duration"] = (
            data["stays_in_weekend_nights"]
            +
            data["stays_in_week_nights"]
        )

    else:

        data["stay_duration"] = 0

    # =============================================================================================
    # ESTIMATED REVENUE
    # =============================================================================================

    if "adr" in data.columns:

        data["estimated_revenue"] = (
            data["adr"].fillna(0)
            *
            data["stay_duration"]
        )

    else:

        data["estimated_revenue"] = 0

    # =============================================================================================
    # LEAD TIME GROUPS
    # =============================================================================================

    data["Lead Time Group"] = pd.cut(
        data["lead_time"],
        bins=[
            -1,
            7,
            30,
            60,
            90,
            180,
            float("inf")
        ],
        labels=[
            "0–7 days",
            "8–30 days",
            "31–60 days",
            "61–90 days",
            "91–180 days",
            "180+ days"
        ],
        include_lowest=True
    )

    # =============================================================================================
    # KPIs
    # =============================================================================================

    average_lead_time = data["lead_time"].mean()
    median_lead_time = data["lead_time"].median()
    maximum_lead_time = data["lead_time"].max()
    minimum_lead_time = data["lead_time"].min()

    cancellation_rate = (
        data["is_canceled"].mean() * 100
        if len(data) > 0
        else 0
    )

    # =============================================================================================
    # KPI DISPLAY
    # =============================================================================================

    st.markdown(
        """
        <h3 style="color: white; font-weight: bold;">
            📌 Lead Time KPIs
        </h3>
        """,
        unsafe_allow_html=True
    )

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi4, kpi5 = st.columns(2)

    with kpi1:

        st.metric(
            "Average Lead Time",
            f"{average_lead_time:.1f} days"
        )

    with kpi2:

        st.metric(
            "Median Lead Time",
            f"{median_lead_time:.1f} days"
        )

    with kpi3:

        st.metric(
            "Maximum Lead Time",
            f"{maximum_lead_time:,.0f} days"
        )

    with kpi4:

        st.metric(
            "Minimum Lead Time",
            f"{minimum_lead_time:,.0f} days"
        )

    with kpi5:

        st.metric(
            "Cancellation Rate",
            f"{cancellation_rate:.2f}%"
        )

    st.divider()

    # =============================================================================================
    # LEAD TIME DISTRIBUTION
    # =============================================================================================

    st.markdown(
        "### 📊 Lead Time Distribution"
    )

    fig = px.histogram(
        data,
        x="lead_time",
        nbins=40,
        labels={
            "lead_time": "Lead Time (Days)"
        }
    )

    fig.update_layout(
        xaxis_title="Lead Time (Days)",
        yaxis_title="Number of Bookings"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # =============================================================================================
    # LEAD TIME BY HOTEL
    # =============================================================================================

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "### 🏨 Lead Time by Hotel"
        )

        if "hotel" in data.columns:

            fig = px.box(
                data,
                x="hotel",
                y="lead_time",
                points=False
            )

            fig.update_layout(
                xaxis_title="Hotel",
                yaxis_title="Lead Time (Days)"
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.info(
                "Hotel column is not available."
            )

    # =============================================================================================
    # LEAD TIME VS CANCELLATION
    # =============================================================================================

    with col2:

        st.markdown(
            "### ❌ Lead Time vs Cancellation"
        )

        lead_cancel = (
            data.groupby(
                "Lead Time Group",
                observed=True
            )
            .agg(
                Bookings=("is_canceled", "size"),
                Cancellation_Rate=("is_canceled", "mean")
            )
            .reset_index()
        )

        lead_cancel["Cancellation Rate"] = (
            lead_cancel["Cancellation_Rate"] * 100
        )

        fig = px.bar(
            lead_cancel,
            x="Lead Time Group",
            y="Cancellation Rate",
            text="Cancellation Rate"
        )

        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )

        fig.update_layout(
            xaxis_title="Lead Time Group",
            yaxis_title="Cancellation Rate (%)"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    # =============================================================================================
    # LEAD TIME BY MARKET SEGMENT
    # =============================================================================================

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "### 📢 Lead Time by Market Segment"
        )

        if "market_segment" in data.columns:

            segment_lead = (
                data.groupby(
                    "market_segment"
                )["lead_time"]
                .mean()
                .reset_index()
            )

            fig = px.bar(
                segment_lead,
                x="market_segment",
                y="lead_time",
                text="lead_time"
            )

            fig.update_traces(
                texttemplate="%{text:.1f}",
                textposition="outside"
            )

            fig.update_layout(
                xaxis_title="Market Segment",
                yaxis_title="Average Lead Time (Days)"
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.info(
                "Market segment column is not available."
            )

    # =============================================================================================
    # LEAD TIME BY CUSTOMER TYPE
    # =============================================================================================

    with col2:

        st.markdown(
            "### 👥 Lead Time by Customer Type"
        )

        if "customer_type" in data.columns:

            customer_lead = (
                data.groupby(
                    "customer_type"
                )["lead_time"]
                .mean()
                .reset_index()
            )

            fig = px.bar(
                customer_lead,
                x="customer_type",
                y="lead_time",
                text="lead_time"
            )

            fig.update_traces(
                texttemplate="%{text:.1f}",
                textposition="outside"
            )

            fig.update_layout(
                xaxis_title="Customer Type",
                yaxis_title="Average Lead Time (Days)"
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.info(
                "Customer type column is not available."
            )

    # =============================================================================================
    # LEAD TIME VS ADR
    # =============================================================================================

    st.markdown(
        "### 💰 Lead Time vs ADR"
    )

    if "adr" in data.columns:

        adr_data = data[
            data["adr"].notna()
        ].copy()

        # Limit extreme ADR values only for visualization
        if not adr_data.empty:

            fig = px.scatter(
                adr_data,
                x="lead_time",
                y="adr",
                opacity=0.35,
                trendline="ols"
            )

            fig.update_layout(
                xaxis_title="Lead Time (Days)",
                yaxis_title="ADR"
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

    else:

        st.info(
            "ADR column is not available."
        )

    # =============================================================================================
    # LEAD TIME GROUP SUMMARY
    # =============================================================================================

    st.markdown(
        "### 📋 Lead-Time Group Performance"
    )

    group_summary = (
        data.groupby(
            "Lead Time Group",
            observed=True
        )
        .agg(
            Bookings=("lead_time", "size"),
            Cancellation_Rate=("is_canceled", "mean"),
            Average_ADR=("adr", "mean"),
            Estimated_Revenue=("estimated_revenue", "sum")
        )
        .reset_index()
    )

    group_summary["Cancellation Rate"] = (
        group_summary["Cancellation_Rate"] * 100
    )

    group_summary = group_summary.drop(
        columns=["Cancellation_Rate"]
    )

    group_summary["Average ADR"] = (
        group_summary["Average_ADR"].round(2)
    )

    group_summary["Estimated Revenue"] = (
        group_summary["Estimated_Revenue"].round(2)
    )

    group_summary = group_summary.drop(
        columns=["Average_ADR", "Estimated_Revenue"]
    )

    st.dataframe(
        group_summary,
        width="stretch",
        hide_index=True
    )

    # =============================================================================================
    # LEAD TIME GROUP BOOKING VOLUME
    # =============================================================================================

    st.markdown(
        "### 📦 Bookings by Lead-Time Group"
    )

    booking_groups = (
        data.groupby(
            "Lead Time Group",
            observed=True
        )
        .size()
        .reset_index(
            name="Bookings"
        )
    )

    fig = px.bar(
        booking_groups,
        x="Lead Time Group",
        y="Bookings",
        text="Bookings"
    )

    fig.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig.update_layout(
        xaxis_title="Lead Time Group",
        yaxis_title="Bookings"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # =============================================================================================
    # DYNAMIC INSIGHTS
    # =============================================================================================

    st.divider()

    st.markdown(
        "### 📌 Key Lead-Time Insights"
    )

    insights = []

    # Highest cancellation group
    lead_rates = (
        data.groupby(
            "Lead Time Group",
            observed=True
        )["is_canceled"]
        .mean()
        .mul(100)
    )

    if not lead_rates.empty:

        highest_cancel_group = lead_rates.idxmax()
        highest_cancel_rate = lead_rates.max()

        insights.append(
            f"❌ **{highest_cancel_group}** has the highest cancellation "
            f"rate at **{highest_cancel_rate:.1f}%**."
        )

    # Average lead time
    insights.append(
        f"⏳ Customers book an average of **{average_lead_time:.1f} days** "
        f"before their arrival."
    )

    # Median vs average
    if average_lead_time > median_lead_time:

        insights.append(
            "📊 The average lead time is higher than the median, "
            "indicating that some bookings are made far in advance."
        )

    # Long booking risk
    long_lead = data[
        data["lead_time"] > 180
    ]

    short_lead = data[
        data["lead_time"] <= 30
    ]

    if not long_lead.empty and not short_lead.empty:

        long_cancel = (
            long_lead["is_canceled"].mean() * 100
        )

        short_cancel = (
            short_lead["is_canceled"].mean() * 100
        )

        if long_cancel > short_cancel:

            insights.append(
                f"⚠️ Bookings made more than **180 days in advance** "
                f"have a higher cancellation rate "
                f"(**{long_cancel:.1f}%**) than bookings made within "
                f"30 days (**{short_cancel:.1f}%**)."
            )

        else:

            insights.append(
                f"✅ Long-lead bookings do not show a higher cancellation "
                f"rate than short-lead bookings in the current dataset."
            )

    # Highest volume group
    volume = (
        data.groupby(
            "Lead Time Group",
            observed=True
        ).size()
    )

    if not volume.empty:

        highest_volume_group = volume.idxmax()

        insights.append(
            f"📦 The **{highest_volume_group}** group contains the "
            f"largest number of bookings."
        )

    for insight in insights[:5]:

        st.info(insight)

    # =============================================================================================
    # RECOMMENDATIONS
    # =============================================================================================

    st.markdown(
        "### 💡 Business Recommendations"
    )

    recommendations = [
        "🎯 Monitor long-lead-time bookings closely when they demonstrate higher cancellation risk.",
        "💳 Consider deposit or stricter cancellation policies for high-risk advance bookings.",
        "📧 Send automated confirmation and reminder messages well before arrival.",
        "💰 Use lead-time patterns to support dynamic pricing and early-booking promotions.",
        "📊 Compare lead-time behavior across market segments and customer types when allocating marketing resources."
    ]

    for recommendation in recommendations:

        st.success(
            recommendation
        )

# =================================================================================================
# 🛏️ STAY DURATION ANALYSIS PAGE
# =================================================================================================

def render_stay_duration_analysis_page(df):

    if df is None or df.empty:
        st.info("📂 Please upload and prepare your dataset first.")
        return

    data = df.copy()

    # =============================================================================================
    # PAGE HEADER
    # =============================================================================================

    st.markdown(
        """
        <h2 style="
            color: white;
            font-weight: bold;
            text-align: center;
            font-size: 40px;
            margin-bottom: 0.25rem;
        ">
            🛏️ Stay Duration Analysis
        </h2>

        <p style="
            color: white;
            margin-top: 0;
        ">
            Analyze how long guests stay, how stay duration differs across
            customer groups, and its relationship with cancellations and ADR.
        </p>
        """,
        unsafe_allow_html=True
    )

    # =============================================================================================
    # REQUIRED COLUMNS / DATA PREPARATION
    # =============================================================================================

    if "stay_duration" in data.columns:

        data["stay_duration"] = pd.to_numeric(
            data["stay_duration"],
            errors="coerce"
        )

    else:

        if all(
            col in data.columns
            for col in [
                "stays_in_weekend_nights",
                "stays_in_week_nights"
            ]
        ):

            data["stays_in_weekend_nights"] = pd.to_numeric(
                data["stays_in_weekend_nights"],
                errors="coerce"
            ).fillna(0)

            data["stays_in_week_nights"] = pd.to_numeric(
                data["stays_in_week_nights"],
                errors="coerce"
            ).fillna(0)

            data["stay_duration"] = (
                data["stays_in_weekend_nights"]
                + data["stays_in_week_nights"]
            )

        else:

            data["stay_duration"] = 0

    data["stay_duration"] = data["stay_duration"].fillna(0)
    data["stay_duration"] = data["stay_duration"].clip(lower=0)

    # =============================================================================================
    # CANCELLATION
    # =============================================================================================

    if "is_canceled" in data.columns:

        data["is_canceled"] = pd.to_numeric(
            data["is_canceled"],
            errors="coerce"
        ).fillna(0)

        data["is_canceled"] = data[
            "is_canceled"
        ].astype(int)

    else:

        data["is_canceled"] = 0

    # =============================================================================================
    # ADR
    # =============================================================================================

    if "adr" in data.columns:

        data["adr"] = pd.to_numeric(
            data["adr"],
            errors="coerce"
        )

    else:

        data["adr"] = 0

    # =============================================================================================
    # ESTIMATED REVENUE
    # =============================================================================================

    data["estimated_revenue"] = (
        data["adr"].fillna(0)
        *
        data["stay_duration"]
    )

    # =============================================================================================
    # STAY GROUPS
    # =============================================================================================

    data["Stay Group"] = pd.cut(
        data["stay_duration"],
        bins=[
            0,
            1,
            3,
            7,
            14,
            float("inf")
        ],
        labels=[
            "1 night",
            "2–3 nights",
            "4–7 nights",
            "8–14 nights",
            "15+ nights"
        ],
        include_lowest=True
    )

    # =============================================================================================
    # KPIs
    # =============================================================================================

    average_stay = data[
        "stay_duration"
    ].mean()

    median_stay = data[
        "stay_duration"
    ].median()

    maximum_stay = data[
        "stay_duration"
    ].max()

    minimum_stay = data[
        "stay_duration"
    ].min()

    long_stay_bookings = (
        (data["stay_duration"] >= 8).sum()
    )

    long_stay_percentage = (
        long_stay_bookings
        /
        len(data)
        *
        100
        if len(data) > 0
        else 0
    )

    # =============================================================================================
    # KPI DISPLAY
    # =============================================================================================

    st.markdown(
        """
        <h3 style="color: white; font-weight: bold;">
            📌 Stay Duration KPIs
        </h3>
        """,
        unsafe_allow_html=True
    )

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi4, kpi5 = st.columns(2)

    with kpi1:

        st.metric(
            "Average Stay",
            f"{average_stay:.1f} nights"
        )

    with kpi2:

        st.metric(
            "Median Stay",
            f"{median_stay:.1f} nights"
        )

    with kpi3:

        st.metric(
            "Maximum Stay",
            f"{maximum_stay:,.0f} nights"
        )

    with kpi4:

        st.metric(
            "Minimum Stay",
            f"{minimum_stay:,.0f} nights"
        )

    with kpi5:

        st.metric(
            "Long-Stay Booking %",
            f"{long_stay_percentage:.2f}%"
        )

    st.divider()

    # =============================================================================================
    # STAY DURATION DISTRIBUTION
    # =============================================================================================

    st.markdown(
        "### 📊 Stay Duration Distribution"
    )

    fig = px.histogram(
        data,
        x="stay_duration",
        nbins=30,
        labels={
            "stay_duration": "Stay Duration (Nights)"
        }
    )

    fig.update_layout(
        xaxis_title="Stay Duration (Nights)",
        yaxis_title="Number of Bookings"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # =============================================================================================
    # STAY DURATION BY HOTEL
    # =============================================================================================

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "### 🏨 Stay Duration by Hotel"
        )

        if "hotel" in data.columns:

            fig = px.box(
                data,
                x="hotel",
                y="stay_duration",
                points=False
            )

            fig.update_layout(
                xaxis_title="Hotel",
                yaxis_title="Stay Duration (Nights)"
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.info(
                "Hotel column is not available."
            )

    # =============================================================================================
    # STAY DURATION VS CANCELLATION
    # =============================================================================================

    with col2:

        st.markdown(
            "### ❌ Stay Duration vs Cancellation"
        )

        stay_cancel = (
            data.groupby(
                "Stay Group",
                observed=True
            )
            .agg(
                Bookings=("is_canceled", "size"),
                Cancellation_Rate=("is_canceled", "mean")
            )
            .reset_index()
        )

        stay_cancel["Cancellation Rate"] = (
            stay_cancel["Cancellation_Rate"] * 100
        )

        fig = px.bar(
            stay_cancel,
            x="Stay Group",
            y="Cancellation Rate",
            text="Cancellation Rate"
        )

        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )

        fig.update_layout(
            xaxis_title="Stay Duration",
            yaxis_title="Cancellation Rate (%)"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    # =============================================================================================
    # STAY DURATION BY CUSTOMER TYPE
    # =============================================================================================

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "### 👥 Stay Duration by Customer Type"
        )

        if "customer_type" in data.columns:

            customer_stay = (
                data.groupby(
                    "customer_type"
                )["stay_duration"]
                .mean()
                .reset_index()
            )

            fig = px.bar(
                customer_stay,
                x="customer_type",
                y="stay_duration",
                text="stay_duration"
            )

            fig.update_traces(
                texttemplate="%{text:.1f}",
                textposition="outside"
            )

            fig.update_layout(
                xaxis_title="Customer Type",
                yaxis_title="Average Stay (Nights)"
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.info(
                "Customer type column is not available."
            )

    # =============================================================================================
    # STAY DURATION BY MARKET SEGMENT
    # =============================================================================================

    with col2:

        st.markdown(
            "### 📢 Stay Duration by Market Segment"
        )

        if "market_segment" in data.columns:

            segment_stay = (
                data.groupby(
                    "market_segment"
                )["stay_duration"]
                .mean()
                .reset_index()
            )

            fig = px.bar(
                segment_stay,
                x="market_segment",
                y="stay_duration",
                text="stay_duration"
            )

            fig.update_traces(
                texttemplate="%{text:.1f}",
                textposition="outside"
            )

            fig.update_layout(
                xaxis_title="Market Segment",
                yaxis_title="Average Stay (Nights)"
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.info(
                "Market segment column is not available."
            )

    # =============================================================================================
    # STAY DURATION VS ADR
    # =============================================================================================

    st.markdown(
        "### 💰 Stay Duration vs ADR"
    )

    adr_data = data[
        data["adr"].notna()
    ].copy()

    if not adr_data.empty:

        fig = px.scatter(
            adr_data,
            x="stay_duration",
            y="adr",
            opacity=0.35,
            trendline="ols"
        )

        fig.update_layout(
            xaxis_title="Stay Duration (Nights)",
            yaxis_title="ADR"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    else:

        st.info(
            "ADR data is not available."
        )

    # =============================================================================================
    # STAY GROUP SUMMARY
    # =============================================================================================

    st.markdown(
        "### 📋 Stay Group Performance"
    )

    stay_summary = (
        data.groupby(
            "Stay Group",
            observed=True
        )
        .agg(
            Bookings=("stay_duration", "size"),
            Cancellation_Rate=("is_canceled", "mean"),
            Average_ADR=("adr", "mean"),
            Estimated_Revenue=("estimated_revenue", "sum")
        )
        .reset_index()
    )

    stay_summary["Cancellation Rate"] = (
        stay_summary["Cancellation_Rate"] * 100
    )

    stay_summary["Average ADR"] = (
        stay_summary["Average_ADR"].round(2)
    )

    stay_summary["Estimated Revenue"] = (
        stay_summary["Estimated_Revenue"].round(2)
    )

    stay_summary = stay_summary.drop(
        columns=[
            "Cancellation_Rate",
            "Average_ADR",
            "Estimated_Revenue"
        ],
        errors="ignore"
    )

    st.dataframe(
        stay_summary,
        width="stretch",
        hide_index=True
    )

    # =============================================================================================
    # BOOKINGS BY STAY GROUP
    # =============================================================================================

    st.markdown(
        "### 📦 Bookings by Stay Group"
    )

    booking_groups = (
        data.groupby(
            "Stay Group",
            observed=True
        )
        .size()
        .reset_index(
            name="Bookings"
        )
    )

    fig = px.bar(
        booking_groups,
        x="Stay Group",
        y="Bookings",
        text="Bookings"
    )

    fig.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig.update_layout(
        xaxis_title="Stay Duration",
        yaxis_title="Bookings"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # =============================================================================================
    # DYNAMIC INSIGHTS
    # =============================================================================================

    st.divider()

    st.markdown(
        "### 📌 Key Stay Duration Insights"
    )

    insights = []

    # Most common stay group
    stay_volume = (
        data.groupby(
            "Stay Group",
            observed=True
        ).size()
    )

    if not stay_volume.empty:

        most_common_group = stay_volume.idxmax()
        most_common_count = stay_volume.max()

        insights.append(
            f"📊 **{most_common_group}** is the most common stay "
            f"duration, accounting for **{most_common_count:,} bookings**."
        )

    # Average stay
    insights.append(
        f"🛏️ Guests stay an average of **{average_stay:.1f} nights**."
    )

    # Highest cancellation group
    stay_cancel_rates = (
        data.groupby(
            "Stay Group",
            observed=True
        )["is_canceled"]
        .mean()
        .mul(100)
    )

    if not stay_cancel_rates.empty:

        highest_cancel_group = stay_cancel_rates.idxmax()
        highest_cancel_rate = stay_cancel_rates.max()

        insights.append(
            f"❌ The **{highest_cancel_group}** group has the highest "
            f"cancellation rate at **{highest_cancel_rate:.1f}%**."
        )

    # Highest ADR group
    stay_adr = (
        data.groupby(
            "Stay Group",
            observed=True
        )["adr"]
        .mean()
    )

    if not stay_adr.empty:

        highest_adr_group = stay_adr.idxmax()
        highest_adr = stay_adr.max()

        insights.append(
            f"💰 **{highest_adr_group}** has the highest average "
            f"ADR at **{highest_adr:.2f}**."
        )

    # Long stay insight
    if long_stay_percentage > 0:

        insights.append(
            f"📅 **{long_stay_percentage:.1f}%** of bookings are "
            f"long-stay bookings of 8 nights or more."
        )

    for insight in insights[:5]:

        st.info(insight)

    # =============================================================================================
    # BUSINESS RECOMMENDATIONS
    # =============================================================================================

    st.markdown(
        "### 💡 Business Recommendations"
    )

    recommendations = [
        "🎯 Monitor stay groups with unusually high cancellation rates and consider targeted cancellation policies.",
        "🏨 Develop packages around the most common stay durations to improve conversion.",
        "💰 Use stay-duration patterns alongside ADR to identify opportunities for longer-stay pricing strategies.",
        "👨‍👩‍👧 Create family or extended-stay packages where longer stays are common.",
        "📊 Monitor long-stay bookings because they can generate substantial estimated revenue but may also create greater cancellation exposure."
    ]

    for recommendation in recommendations:

        st.success(
            recommendation
        )

# ============================================================
# CREATE STAY DURATION
# ============================================================
prepared_df = df.copy()
# Make sure both source columns are numeric
df["stays_in_weekend_nights"] = pd.to_numeric(
    df["stays_in_weekend_nights"],
    errors="coerce"
)

df["stays_in_week_nights"] = pd.to_numeric(
    df["stays_in_week_nights"],
    errors="coerce"
)

# Replace missing values with 0
df["stays_in_weekend_nights"] = (
    df["stays_in_weekend_nights"].fillna(0)
)

df["stays_in_week_nights"] = (
    df["stays_in_week_nights"].fillna(0)
)

# Create total stay duration
df["stay_duration"] = (
    df["stays_in_weekend_nights"]
    +
    df["stays_in_week_nights"]
)

# Make sure duration cannot be negative
df["stay_duration"] = (
    df["stay_duration"].clip(lower=0)
)

# =================================================================================================
# 💰 REVENUE ANALYSIS PAGE
# =================================================================================================

def render_revenue_analysis_page(df):

    if df is None or df.empty:
        st.info("📂 Please upload and prepare your dataset first.")
        return

    data = df.copy()

    # =============================================================================================
    # PAGE HEADER
    # =============================================================================================

    st.markdown(
        """
        <h2 style="
            color: white;
            font-weight: bold;
            text-align: center;
            font-size: 40px;
            margin-bottom: 0.25rem;
        ">
            💰 Revenue Analysis
        </h2>

        <p style="
            color: white;
            margin-top: 0;
        ">
            Analyze estimated hotel revenue, ADR performance, revenue trends,
            and revenue exposure from cancelled bookings.
        </p>
        """,
        unsafe_allow_html=True
    )

    # =============================================================================================
    # REQUIRED ADR COLUMN
    # =============================================================================================

    if "adr" not in data.columns:

        st.error(
            "❌ The required 'adr' column is not available in the prepared dataset."
        )

        return

    # =============================================================================================
    # ADR PREPARATION
    # =============================================================================================

    data["adr"] = pd.to_numeric(
        data["adr"],
        errors="coerce"
    )

    data = data.dropna(
        subset=["adr"]
    ).copy()

    # Remove negative ADR values
    data["adr"] = data["adr"].clip(lower=0)

    # =============================================================================================
    # STAY DURATION
    # =============================================================================================

    if "stay_duration" in data.columns:

        data["stay_duration"] = pd.to_numeric(
            data["stay_duration"],
            errors="coerce"
        ).fillna(0)

    elif (
        "stays_in_weekend_nights" in data.columns
        and
        "stays_in_week_nights" in data.columns
    ):

        data["stay_duration"] = (
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

        st.error(
            "❌ Stay duration information is not available. "
            "Please create the 'stay_duration' column during data preparation."
        )

        return

    # =============================================================================================
    # CANCELLATION
    # =============================================================================================

    if "is_canceled" in data.columns:

        data["is_canceled"] = pd.to_numeric(
            data["is_canceled"],
            errors="coerce"
        ).fillna(0)

        data["is_canceled"] = data[
            "is_canceled"
        ].astype(int)

    else:

        data["is_canceled"] = 0

    # =============================================================================================
    # ESTIMATED REVENUE
    # =============================================================================================

    data["estimated_revenue"] = (
        data["adr"]
        *
        data["stay_duration"]
    )

    # =============================================================================================
    # CANCELLED REVENUE
    # =============================================================================================

    data["cancelled_revenue"] = (
        data["estimated_revenue"]
        *
        data["is_canceled"]
    )

    # =============================================================================================
    # CONFIRMED REVENUE
    # =============================================================================================

    data["confirmed_revenue"] = (
        data["estimated_revenue"]
        *
        (1 - data["is_canceled"])
    )

    # =============================================================================================
    # KPI CALCULATIONS
    # =============================================================================================

    total_estimated_revenue = data[
        "estimated_revenue"
    ].sum()

    average_adr = data[
        "adr"
    ].mean()

    median_adr = data[
        "adr"
    ].median()

    maximum_adr = data[
        "adr"
    ].max()

    cancelled_revenue = data[
        "cancelled_revenue"
    ].sum()

    confirmed_revenue = data[
        "confirmed_revenue"
    ].sum()

    # =============================================================================================
    # REVENUE EXPOSURE %
    # =============================================================================================

    revenue_exposure = (
        cancelled_revenue
        /
        total_estimated_revenue
        *
        100
        if total_estimated_revenue > 0
        else 0
    )

    # =============================================================================================
    # KPI DISPLAY
    # =============================================================================================

    st.markdown(
        """
        <h3 style="color: white; font-weight: bold;">
            📌 Revenue KPIs
        </h3>
        """,
        unsafe_allow_html=True
    )

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi4, kpi5 = st.columns(2)

    with kpi1:

        st.metric(
            "Estimated Revenue",
            f"{total_estimated_revenue:,.2f}"
        )

    with kpi2:

        st.metric(
            "Average ADR",
            f"{average_adr:,.2f}"
        )

    with kpi3:

        st.metric(
            "Median ADR",
            f"{median_adr:,.2f}"
        )

    with kpi4:

        st.metric(
            "Maximum ADR",
            f"{maximum_adr:,.2f}"
        )

    with kpi5:

        st.metric(
            "Revenue Exposed to Cancellation",
            f"{revenue_exposure:.2f}%"
        )

    st.divider()

    # =============================================================================================
    # REVENUE BY HOTEL
    # =============================================================================================

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "### 🏨 Revenue by Hotel"
        )

        if "hotel" in data.columns:

            hotel_revenue = (
                data.groupby("hotel")[
                    "estimated_revenue"
                ]
                .sum()
                .reset_index()
            )

            fig = px.bar(
                hotel_revenue,
                x="hotel",
                y="estimated_revenue",
                text="estimated_revenue"
            )

            fig.update_traces(
                texttemplate="%{text:,.0f}",
                textposition="outside"
            )

            fig.update_layout(
                xaxis_title="Hotel",
                yaxis_title="Estimated Revenue"
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.info(
                "Hotel column is not available."
            )

    # =============================================================================================
    # ADR BY HOTEL
    # =============================================================================================

    with col2:

        st.markdown(
            "### 💵 ADR by Hotel"
        )

        if "hotel" in data.columns:

            hotel_adr = (
                data.groupby("hotel")[
                    "adr"
                ]
                .mean()
                .reset_index()
            )

            fig = px.bar(
                hotel_adr,
                x="hotel",
                y="adr",
                text="adr"
            )

            fig.update_traces(
                texttemplate="%{text:.2f}",
                textposition="outside"
            )

            fig.update_layout(
                xaxis_title="Hotel",
                yaxis_title="Average ADR"
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.info(
                "Hotel column is not available."
            )

    # =============================================================================================
    # MONTHLY REVENUE
    # =============================================================================================

    st.markdown(
        "### 📅 Monthly Estimated Revenue"
    )

    if "arrival_date_month" in data.columns:

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

        monthly_revenue = (
            data.groupby(
                "arrival_date_month"
            )["estimated_revenue"]
            .sum()
            .reset_index()
        )

        monthly_revenue["arrival_date_month"] = pd.Categorical(
            monthly_revenue["arrival_date_month"],
            categories=month_order,
            ordered=True
        )

        monthly_revenue = monthly_revenue.sort_values(
            "arrival_date_month"
        )

        fig = px.line(
            monthly_revenue,
            x="arrival_date_month",
            y="estimated_revenue",
            markers=True
        )

        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Estimated Revenue"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    else:

        st.info(
            "Arrival month column is not available."
        )

    # =============================================================================================
    # ADR BY MONTH
    # =============================================================================================

    st.markdown(
        "### 📈 ADR by Month"
    )

    if "arrival_date_month" in data.columns:

        monthly_adr = (
            data.groupby(
                "arrival_date_month"
            )["adr"]
            .mean()
            .reset_index()
        )

        monthly_adr["arrival_date_month"] = pd.Categorical(
            monthly_adr["arrival_date_month"],
            categories=month_order,
            ordered=True
        )

        monthly_adr = monthly_adr.sort_values(
            "arrival_date_month"
        )

        fig = px.line(
            monthly_adr,
            x="arrival_date_month",
            y="adr",
            markers=True
        )

        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Average ADR"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    # =============================================================================================
    # REVENUE BY MARKET SEGMENT
    # =============================================================================================

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "### 📢 Revenue by Market Segment"
        )

        if "market_segment" in data.columns:

            segment_revenue = (
                data.groupby(
                    "market_segment"
                )["estimated_revenue"]
                .sum()
                .reset_index()
                .sort_values(
                    "estimated_revenue",
                    ascending=False
                )
            )

            fig = px.bar(
                segment_revenue,
                x="market_segment",
                y="estimated_revenue",
                text="estimated_revenue"
            )

            fig.update_traces(
                texttemplate="%{text:,.0f}",
                textposition="outside"
            )

            fig.update_layout(
                xaxis_title="Market Segment",
                yaxis_title="Estimated Revenue"
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.info(
                "Market segment column is not available."
            )

    # =============================================================================================
    # REVENUE BY CUSTOMER TYPE
    # =============================================================================================

    with col2:

        st.markdown(
            "### 👥 Revenue by Customer Type"
        )

        if "customer_type" in data.columns:

            customer_revenue = (
                data.groupby(
                    "customer_type"
                )["estimated_revenue"]
                .sum()
                .reset_index()
                .sort_values(
                    "estimated_revenue",
                    ascending=False
                )
            )

            fig = px.bar(
                customer_revenue,
                x="customer_type",
                y="estimated_revenue",
                text="estimated_revenue"
            )

            fig.update_traces(
                texttemplate="%{text:,.0f}",
                textposition="outside"
            )

            fig.update_layout(
                xaxis_title="Customer Type",
                yaxis_title="Estimated Revenue"
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        else:

            st.info(
                "Customer type column is not available."
            )

    # =============================================================================================
    # ADR DISTRIBUTION
    # =============================================================================================

    st.markdown(
        "### 📊 ADR Distribution"
    )

    fig = px.histogram(
        data,
        x="adr",
        nbins=40
    )

    fig.update_layout(
        xaxis_title="ADR",
        yaxis_title="Number of Bookings"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # =============================================================================================
    # REVENUE LOST TO CANCELLATION
    # =============================================================================================

    st.markdown(
        "### ❌ Estimated Revenue Lost to Cancellation"
    )

    cancellation_revenue = (
        data.groupby("is_canceled")[
            "estimated_revenue"
        ]
        .sum()
        .reset_index()
    )

    cancellation_revenue["Booking Status"] = (
        cancellation_revenue["is_canceled"]
        .map({
            0: "Confirmed",
            1: "Cancelled"
        })
    )

    fig = px.bar(
        cancellation_revenue,
        x="Booking Status",
        y="estimated_revenue",
        text="estimated_revenue"
    )

    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside"
    )

    fig.update_layout(
        xaxis_title="Booking Status",
        yaxis_title="Estimated Revenue"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # =============================================================================================
    # ADR VS CANCELLATION
    # =============================================================================================

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "### ❌ ADR vs Cancellation"
        )

        cancellation_adr = (
            data.groupby("is_canceled")[
                "adr"
            ]
            .mean()
            .reset_index()
        )

        cancellation_adr["Booking Status"] = (
            cancellation_adr["is_canceled"]
            .map({
                0: "Confirmed",
                1: "Cancelled"
            })
        )

        fig = px.bar(
            cancellation_adr,
            x="Booking Status",
            y="adr",
            text="adr"
        )

        fig.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside"
        )

        fig.update_layout(
            xaxis_title="Booking Status",
            yaxis_title="Average ADR"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    # =============================================================================================
    # REVENUE BY CUSTOMER TYPE
    # =============================================================================================

    with col2:

        st.markdown(
            "### 🛏️ Revenue by Stay Duration"
        )

        data["Stay Group"] = pd.cut(
            data["stay_duration"],
            bins=[
                0,
                1,
                3,
                7,
                14,
                float("inf")
            ],
            labels=[
                "1 night",
                "2–3 nights",
                "4–7 nights",
                "8–14 nights",
                "15+ nights"
            ],
            include_lowest=True
        )

        stay_revenue = (
            data.groupby(
                "Stay Group",
                observed=True
            )["estimated_revenue"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            stay_revenue,
            x="Stay Group",
            y="estimated_revenue",
            text="estimated_revenue"
        )

        fig.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside"
        )

        fig.update_layout(
            xaxis_title="Stay Duration",
            yaxis_title="Estimated Revenue"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    # =============================================================================================
    # REVENUE SUMMARY TABLE
    # =============================================================================================

    st.markdown(
        "### 📋 Revenue Summary"
    )

    summary_data = {
        "Metric": [
            "Estimated Revenue",
            "Confirmed Revenue",
            "Estimated Cancelled Revenue",
            "Revenue Exposure",
            "Average ADR",
            "Median ADR",
            "Maximum ADR"
        ],
        "Value": [
            f"{total_estimated_revenue:,.2f}",
            f"{confirmed_revenue:,.2f}",
            f"{cancelled_revenue:,.2f}",
            f"{revenue_exposure:.2f}%",
            f"{average_adr:,.2f}",
            f"{median_adr:,.2f}",
            f"{maximum_adr:,.2f}"
        ]
    }

    revenue_summary = pd.DataFrame(
        summary_data
    )

    st.dataframe(
        revenue_summary,
        width="stretch",
        hide_index=True
    )

    # =============================================================================================
    # DYNAMIC BUSINESS INSIGHTS
    # =============================================================================================

    st.divider()

    st.markdown(
        "### 📌 Key Revenue Insights"
    )

    insights = []

    # Highest revenue hotel
    if "hotel" in data.columns:

        hotel_rev = (
            data.groupby("hotel")[
                "estimated_revenue"
            ]
            .sum()
        )

        if not hotel_rev.empty:

            top_hotel = hotel_rev.idxmax()
            top_hotel_revenue = hotel_rev.max()

            insights.append(
                f"🏨 **{top_hotel}** generates the highest estimated "
                f"revenue at **{top_hotel_revenue:,.2f}**."
            )

    # Highest ADR month
    if "arrival_date_month" in data.columns:

        month_adr = (
            data.groupby(
                "arrival_date_month"
            )["adr"]
            .mean()
        )

        if not month_adr.empty:

            top_adr_month = month_adr.idxmax()
            top_adr_value = month_adr.max()

            insights.append(
                f"📈 **{top_adr_month}** has the highest average ADR "
                f"at **{top_adr_value:,.2f}**."
            )

    # Highest revenue segment
    if "market_segment" in data.columns:

        segment_rev = (
            data.groupby(
                "market_segment"
            )["estimated_revenue"]
            .sum()
        )

        if not segment_rev.empty:

            top_segment = segment_rev.idxmax()

            insights.append(
                f"📢 **{top_segment}** contributes the highest "
                f"estimated revenue among market segments."
            )

    # Cancellation exposure
    insights.append(
        f"❌ Approximately **{revenue_exposure:.1f}%** of estimated "
        f"revenue is associated with cancelled bookings."
    )

    # ADR
    insights.append(
        f"💵 The average ADR across the filtered dataset is "
        f"**{average_adr:,.2f}**."
    )

    for insight in insights[:5]:

        st.info(insight)

    # =============================================================================================
    # BUSINESS RECOMMENDATIONS
    # =============================================================================================

    st.markdown(
        "### 💡 Business Recommendations"
    )

    recommendations = [
        "💰 Focus pricing strategies on periods and segments generating strong ADR and revenue.",
        "📈 Consider dynamic pricing during high-demand periods when ADR and booking volume increase.",
        "❌ Monitor revenue exposure from cancelled bookings and consider stronger deposit policies for high-risk bookings.",
        "📢 Prioritize marketing channels and customer segments that generate strong revenue with manageable cancellation levels.",
        "🛏️ Develop longer-stay packages when longer stays demonstrate favorable revenue characteristics."
    ]

    for recommendation in recommendations:

        st.success(
            recommendation
        )

    # =============================================================================================
    # REVENUE DISCLAIMER
    # =============================================================================================

    st.caption(
        "ℹ️ Estimated Revenue = ADR × Stay Duration. "
        "This is an analytical estimate and should not be interpreted as actual "
        "collected hotel revenue."
    )

#===========================================================================================================================================================================================================
#page routing based on selected page
#===========================================================================================================================================================================================================

if selected_page == "📊 Executive Overview":
    render_executive_overview_page(prepared_df)

elif selected_page == "🏨 Hotel Performance":
    render_hotel_performance_page(prepared_df)

elif selected_page == "📅 Booking Trends":
    render_booking_trends_page(prepared_df)

elif selected_page == "❌ Cancellation Analysis":
    render_cancellation_analysis_page(prepared_df)

elif selected_page == "⏳ Lead Time Analysis":
    render_lead_time_analysis_page(prepared_df)

elif selected_page == "🛏️ Stay Duration":
    render_stay_duration_analysis_page(prepared_df)

elif selected_page == "💰 Revenue Analysis":
    render_revenue_analysis_page(prepared_df)