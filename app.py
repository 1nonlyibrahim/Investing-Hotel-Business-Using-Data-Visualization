#====================================================================================
# IMPORT LIBRARY
#====================================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

#====================================================================================
# STREAMLIT PAGE CONFIGURE
#====================================================================================

st.set_page_config(
    page_title="Hotel Booking Analytics Dashboard",
    page_icon="🛎️",
    layout="wide",
)

# ============================================================
# SESSION STATE
# ============================================================

if "data_prepared" not in st.session_state:
    st.session_state.data_prepared = False

if "show_processing" not in st.session_state:
    st.session_state.show_processing = False

if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None

if "uploaded_file_id" not in st.session_state:
    st.session_state.uploaded_file_id = None

if "raw_df" not in st.session_state:
    st.session_state.raw_df = None

if "cleaned_df" not in st.session_state:
    st.session_state.cleaned_df = None

if "original_df" not in st.session_state:
    st.session_state.original_df = None

if "prep_popup_visible" not in st.session_state:
    st.session_state.prep_popup_visible = False

if "prep_popup_title" not in st.session_state:
    st.session_state.prep_popup_title = "Preparing your dataset"

if "prep_popup_step_index" not in st.session_state:
    st.session_state.prep_popup_step_index = 0

if "prep_popup_total_steps" not in st.session_state:
    st.session_state.prep_popup_total_steps = 5

if "prep_popup_status" not in st.session_state:
    st.session_state.prep_popup_status = "running"

if "prep_popup_detail" not in st.session_state:
    st.session_state.prep_popup_detail = ""

if "prep_popup_current_step_name" not in st.session_state:
    st.session_state.prep_popup_current_step_name = None

#====================================================================================
# ALL THE DEF FUNCTIONS ARE DEFINED HERE
#====================================================================================
def show_notification(message, duration=3):
    """
    Displays a reusable animated dark-green notification
    near the top-center of the screen.
    """

    st.markdown(
        f"""
        <style>
        .custom-notification {{
            position: fixed;
            top: 75px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 999999;
            min-width: 380px;
            max-width: 650px;
            padding: 15px 24px;
            background: rgba(5, 35, 20, 0.97);
            border: 1px solid #20ff8a;
            border-radius: 12px;
            color: #20ff8a;
            font-size: 15px;
            font-weight: 600;
            letter-spacing: 0.2px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            animation:
                notification-slide-down 0.5s ease-out forwards,
                notification-slide-up 0.5s ease-in {duration}s forwards;
            pointer-events: none;
        }}

        @keyframes notification-slide-down {{
            0% {{
                opacity: 0;
                transform: translate(-50%, -12px);
            }}
            100% {{
                opacity: 1;
                transform: translate(-50%, 0);
            }}
        }}

        @keyframes notification-slide-up {{
            0% {{
                opacity: 1;
                transform: translate(-50%, 0);
            }}
            100% {{
                opacity: 0;
                transform: translate(-50%, -12px);
            }}
        }}
        </style>

        <div class="custom-notification">
            {message}
        </div>
        """,
        unsafe_allow_html=True
    )

if "pending_notification" not in st.session_state:
    st.session_state["pending_notification"] = None

if st.session_state.get("pending_notification"):
    notification_message = st.session_state["pending_notification"]

    st.session_state["pending_notification"] = None

    show_notification(notification_message)

#====================================================================================

def get_uploaded_file_id(uploaded_file):
    """Create a stable identifier for the uploaded file."""
    if uploaded_file is None:
        return None

    uploaded_file.seek(0)
    file_bytes = uploaded_file.getvalue()
    if not file_bytes:
        return None

    return f"{uploaded_file.name}:{uploaded_file.size}:{hashlib.md5(file_bytes).hexdigest()}"


def render_preparation_popup(step_index, total_steps, status, detail, title="Preparing your dataset", current_step_name=None):
    st.session_state.prep_popup_visible = True
    st.session_state.prep_popup_step_index = step_index
    st.session_state.prep_popup_total_steps = total_steps
    st.session_state.prep_popup_status = status
    st.session_state.prep_popup_detail = detail
    st.session_state.prep_popup_title = title
    st.session_state.prep_popup_current_step_name = current_step_name

    progress_percent = 100 if status == "success" else max(8, int(((step_index + 1) / total_steps) * 100))
    step_names = [
        "Validate required columns",
        "Check missing values",
        "Remove duplicate rows",
        "Fix data types",
        "Finalize dataset",
    ]

    status_styles = {
        "running": ("⏳", "background: #f8fafc; color: #0f172a; border: 1px solid #dbe4f0;"),
        "success": ("✅", "background: #ecfdf3; color: #166534; border: 1px solid #a7f3d0;"),
        "error": ("❌", "background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca;"),
    }

    step_items = []
    for idx, step_name in enumerate(step_names):
        if idx < step_index:
            icon, style = status_styles["success"]
        elif idx == step_index:
            icon, style = status_styles[status]
        else:
            icon, style = ("○", "background: #ffffff; color: #64748b; border: 1px solid #e2e8f0;")

        step_items.append(
            f"<div style='margin-top:10px; padding:12px 14px; border-radius:10px; {style}'>{icon} <strong>{step_name}</strong></div>"
        )

    if status == "error":
        message_box = f"<div style='margin-top:16px; padding:12px 14px; border-radius:10px; background:#fee2e2; color:#991b1b; border:1px solid #fecaca;'>{detail}</div>"
    elif status == "success":
        message_box = f"<div style='margin-top:16px; padding:12px 14px; border-radius:10px; background:#ecfdf3; color:#166534; border:1px solid #a7f3d0;'>{detail}</div>"
    else:
        message_box = f"<div style='margin-top:16px; padding:12px 14px; border-radius:10px; background:#f8fafc; color:#0f172a; border:1px solid #dbe4f0;'>{detail}</div>"

    current_label = current_step_name or (step_names[step_index] if step_index < len(step_names) else "Finishing up")

    html = f"""
    <div style="position:fixed; inset:0; z-index:9999; background:rgba(15,23,42,0.72); display:flex; align-items:center; justify-content:center; padding:24px;">
        <div style="width:min(780px, 100%); background:rgba(255,255,255,0.97); border-radius:18px; padding:24px 28px; box-shadow:0 20px 60px rgba(0,0,0,0.35); border:1px solid rgba(255,255,255,0.25);">
            <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap;">
                <div>
                    <h3 style="margin:0 0 8px; color:#111827; font-size:24px;">{title}</h3>
                    <p style="margin:0; color:#4b5563;">Please wait while we prepare your dataset.</p>
                </div>
                <div style="padding:8px 12px; border-radius:999px; background:#f3f4f6; color:#374151; font-size:13px; font-weight:700;">
                    {current_label}
                </div>
            </div>
            <div style="position:relative; height:10px; width:100%; background:#e5e7eb; border-radius:999px; overflow:hidden; margin-top:14px;">
                <div style="height:100%; width:{progress_percent}%; background:linear-gradient(90deg, #ef4444, #f59e0b, #10b981); border-radius:999px; animation:pulse 1.2s ease-in-out infinite;"></div>
            </div>
            <div style="margin-top:16px;">
                {''.join(step_items)}
            </div>
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
    """Load and set a local image as the background"""
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode()

    page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        position: relative;
        isolation: isolate;
        background: transparent;
    }}

    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        inset: 0;
        background-image: url("data:image/png;base64,{image_data}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        filter: blur(8px);
        transform: scale(1.05);
        z-index: -1;
        pointer-events: none;
    }}

    [data-testid="stAppViewContainer"] > * {{
        position: relative;
        z-index: 1;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)


set_background_image("Abstract red to black gradient background with grainy noise texture for digital design projects.jfif")

#====================================================================================
# HEADER SECTION
#====================================================================================

st.markdown(
    "<h1 style='text-align: center; text-transform: uppercase; color: white; font-weight: 700; font-size: 64px;'>Hotel Booking Analytics Dashboard</h1>",
    unsafe_allow_html=True,
)

#====================================================================================
# UPLOADER BOX
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

#====================================================================================
#  DATASET PREPORCESSING
#====================================================================================

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
    "reservation_status",
]


# ============================================================
# RED GLOWING BUTTON
# ============================================================

should_show_proceed = (
    uploaded_file is not None
    and st.session_state.get("raw_df") is not None
    and not st.session_state.get("data_prepared")
    and not st.session_state.get("show_processing")
)

if st.session_state.get("show_processing") and st.session_state.get("prep_popup_visible"):
    render_preparation_popup(
        st.session_state.get("prep_popup_step_index", 0),
        st.session_state.get("prep_popup_total_steps", 5),
        st.session_state.get("prep_popup_status", "running"),
        st.session_state.get("prep_popup_detail", ""),
        title=st.session_state.get("prep_popup_title", "Preparing your dataset"),
        current_step_name=st.session_state.get("prep_popup_current_step_name"),
    )

if should_show_proceed:
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
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # CENTER BUTTON
    # --------------------------------------------------------

    cols = st.columns([1, 2, 1])

    with cols[1]:
        proceed = st.button(
            "🚀 Proceed with Data Preparation",
            key="open_window",
            use_container_width=True,
        )

    # ========================================================
    # DATA PREPARATION PIPELINE
    # ========================================================

    if proceed:
        st.session_state["show_processing"] = True
        st.session_state["prep_popup_visible"] = True
        st.session_state["data_prepared"] = False

        try:
            df = st.session_state["raw_df"].copy()
        except Exception as e:
            render_preparation_popup(4, 5, "error", f"Preparation failed: {str(e)}", current_step_name="Finalize dataset")
            st.error("❌ Preparation failed.")
            st.caption("The uploaded dataset could not be prepared. Please check the file format and try again.")
            st.session_state["show_processing"] = True
            st.session_state["prep_popup_visible"] = True
            st.session_state["data_prepared"] = False
        else:
            try:
                render_preparation_popup(0, 5, "running", "Checking that all required columns are present.", current_step_name="Validate required columns")
                time.sleep(0.4)

                original_df = df.copy()
                dataset_columns = set(df.columns)
                missing_columns = [column for column in REQUIRED_COLUMNS if column not in dataset_columns]

                if missing_columns:
                    render_preparation_popup(0, 5, "error", f"Missing columns detected: {', '.join(missing_columns)}", current_step_name="Validate required columns")
                    st.error("❌ Dataset validation failed.")
                    st.write("The following required columns are missing:")
                    for column in missing_columns:
                        st.write(f"❌ `{column}`")
                    st.session_state["data_prepared"] = False
                    st.session_state["show_processing"] = True
                    st.session_state["prep_popup_visible"] = True
                else:
                    render_preparation_popup(0, 5, "success", f"All {len(REQUIRED_COLUMNS)} required columns are available.", current_step_name="Validate required columns")
                    time.sleep(0.4)

                    render_preparation_popup(1, 5, "running", "Checking the dataset for missing values.", current_step_name="Check missing values")
                    time.sleep(0.4)

                    missing_before = df.isnull().sum()
                    total_missing_before = missing_before.sum()

                    if total_missing_before > 0:
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
                            "total_of_special_requests",
                        ]

                        for column in numerical_columns:
                            if column in df.columns and df[column].isnull().sum() > 0:
                                df[column] = df[column].fillna(df[column].median())

                        categorical_columns = [
                            "hotel",
                            "arrival_date_month",
                            "meal",
                            "city",
                            "market_segment",
                            "distribution_channel",
                            "deposit_type",
                            "customer_type",
                            "reservation_status",
                        ]

                        for column in categorical_columns:
                            if column in df.columns and df[column].isnull().sum() > 0:
                                mode_value = df[column].mode()
                                if not mode_value.empty:
                                    df[column] = df[column].fillna(mode_value[0])

                        if "agent" in df.columns:
                            df["agent"] = df["agent"].fillna(0)

                        if "company" in df.columns:
                            df["company"] = df["company"].fillna(0)

                    render_preparation_popup(1, 5, "success", "Missing values were checked and handled successfully.", current_step_name="Check missing values")
                    time.sleep(0.4)

                    render_preparation_popup(2, 5, "running", "Checking for duplicate rows.", current_step_name="Remove duplicate rows")
                    time.sleep(0.4)

                    duplicates_before = df.duplicated().sum()
                    if duplicates_before > 0:
                        df = df.drop_duplicates()

                    render_preparation_popup(2, 5, "success", f"Duplicate review completed. Removed {duplicates_before:,} duplicate rows." if duplicates_before > 0 else "No duplicate rows were found.", current_step_name="Remove duplicate rows")
                    time.sleep(0.4)

                    render_preparation_popup(3, 5, "running", "Converting columns to the correct data types.", current_step_name="Fix data types")
                    time.sleep(0.4)

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
                        "total_of_special_requests",
                    ]

                    for column in integer_columns:
                        if column in df.columns:
                            df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0).astype(int)

                    if "adr" in df.columns:
                        df["adr"] = pd.to_numeric(df["adr"], errors="coerce")

                    if "agent" in df.columns:
                        df["agent"] = pd.to_numeric(df["agent"], errors="coerce").fillna(0).astype(int)

                    if "company" in df.columns:
                        df["company"] = pd.to_numeric(df["company"], errors="coerce").fillna(0).astype(int)

                    render_preparation_popup(3, 5, "success", "Data types were converted successfully.", current_step_name="Fix data types")
                    time.sleep(0.4)

                    render_preparation_popup(4, 5, "running", "Finalizing the cleaned dataset.", current_step_name="Finalize dataset")
                    time.sleep(0.4)

                    st.session_state["cleaned_df"] = df
                    st.session_state["original_df"] = original_df
                    st.session_state["data_prepared"] = True

                    render_preparation_popup(4, 5, "success", "Prepared successfully — now proceeding to analysis.", current_step_name="Finalize dataset")
                    time.sleep(1.2)
                    st.session_state["show_processing"] = False
                    st.session_state["prep_popup_visible"] = False
                    st.session_state["prep_popup_status"] = "running"
                    st.session_state["prep_popup_detail"] = ""
                    st.session_state["prep_popup_step_index"] = 0
                    st.session_state["prep_popup_current_step_name"] = None
                    st.session_state["prep_popup_title"] = "Preparing your dataset"
                    st.session_state["prep_popup_total_steps"] = 5
                    st.rerun()
            except Exception as e:
                render_preparation_popup(4, 5, "error", f"Preparation failed: {str(e)}", current_step_name="Finalize dataset")
                st.error("❌ Preparation failed.")
                st.caption("The uploaded dataset could not be prepared. Please check the file format and required columns.")
                st.session_state["show_processing"] = True
                st.session_state["prep_popup_visible"] = True
                st.session_state["data_prepared"] = False
                time.sleep(1.2)
                st.session_state["show_processing"] = False
                st.session_state["prep_popup_visible"] = False
                st.session_state["prep_popup_status"] = "running"
                st.session_state["prep_popup_detail"] = ""
                st.session_state["prep_popup_step_index"] = 0
                st.session_state["prep_popup_current_step_name"] = None
                st.session_state["prep_popup_title"] = "Preparing your dataset"
                st.session_state["prep_popup_total_steps"] = 5
                st.rerun()

if st.session_state.get("show_processing") and st.session_state.get("prep_popup_visible") and st.session_state.get("prep_popup_status") in {"success", "error"}:
    cols = st.columns([1, 2, 1])
    with cols[1]:
        close_preparation = st.button("Close", key="close_preparation_popup", use_container_width=True)

    if close_preparation:
        st.session_state["show_processing"] = False
        st.session_state["prep_popup_visible"] = False
        st.session_state["prep_popup_status"] = "running"
        st.session_state["prep_popup_detail"] = ""
        st.session_state["prep_popup_step_index"] = 0
        st.session_state["prep_popup_current_step_name"] = None
        st.session_state["prep_popup_title"] = "Preparing your dataset"
        st.session_state["prep_popup_total_steps"] = 5
        st.session_state["pending_notification"] = (
            "✅ Preparation successful. You can proceed with the analysis."
        )

        st.rerun()

def prepare_dataset(df):
    """Prepare a dataframe for downstream analysis."""
    if df is None:
        return pd.DataFrame()

    if st.session_state.get("data_prepared") and st.session_state.get("cleaned_df") is not None:
        prepared_df = st.session_state["cleaned_df"].copy()
    else:
        prepared_df = df.copy()

        if prepared_df.empty:
            return prepared_df

        numeric_columns = [
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

        for column in numeric_columns:
            if column in prepared_df.columns:
                prepared_df[column] = pd.to_numeric(prepared_df[column], errors="coerce").fillna(0)

        for column in ["agent", "company"]:
            if column in prepared_df.columns:
                prepared_df[column] = pd.to_numeric(prepared_df[column], errors="coerce").fillna(0).astype(int)

        for column in ["hotel", "arrival_date_month", "meal", "city", "market_segment", "distribution_channel", "deposit_type", "customer_type", "reservation_status"]:
            if column in prepared_df.columns:
                prepared_df[column] = prepared_df[column].fillna("Unknown").astype(str).str.strip()

        prepared_df = prepared_df.drop_duplicates()

    if "stays_in_weekend_nights" in prepared_df.columns and "stays_in_weekdays_nights" in prepared_df.columns:
        prepared_df["total_stay_nights"] = (
            prepared_df["stays_in_weekend_nights"] + prepared_df["stays_in_weekdays_nights"]
        )
    else:
        prepared_df["total_stay_nights"] = 0

    if "adr" in prepared_df.columns and "total_stay_nights" in prepared_df.columns:
        prepared_df["estimated_revenue"] = prepared_df["adr"] * prepared_df["total_stay_nights"]
    else:
        prepared_df["estimated_revenue"] = 0.0

    return prepared_df


def render_data_preparation(df, original_df=None, cleaning_stats=None):
    """Render the data preparation summary page for the current dataset."""
    st.header("🧹 Data Preparation")
    st.markdown("Review the cleaning and transformation steps applied to the uploaded dataset.")

    if df is None:
        st.info("No dataset available for the data preparation view.")
        return

    if original_df is None:
        original_df = df.copy()

    stats = cleaning_stats or {}

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Original Rows", f"{len(original_df):,}")
    with col2:
        st.metric("Prepared Rows", f"{len(df):,}")
    with col3:
        st.metric("Missing Values Fixed", f"{stats.get('missing_values_fixed', 0):,}")
    with col4:
        st.metric("Duplicates Removed", f"{stats.get('duplicates_removed', 0):,}")

    st.subheader("Preparation Summary")
    summary_df = pd.DataFrame(
        [
            {
                "Original Rows": len(original_df),
                "Prepared Rows": len(df),
                "Duplicates Removed": stats.get("duplicates_removed", 0),
                "Missing Values Fixed": stats.get("missing_values_fixed", 0),
                "Invalid Rows Removed": stats.get("invalid_rows_removed", 0),
                "Outliers Removed": stats.get("outliers_removed", 0),
                "Data Types Fixed": stats.get("dtypes_fixed", 0),
            }
        ]
    )
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    st.subheader("Prepared Dataset Preview")
    st.dataframe(df.head(10), use_container_width=True)


def render_dataset_overview(df):
    """Render a dataset overview page for the current dataset."""
    if df is None or df.empty:
        st.info("No dataset available for the dataset overview.")
        return

    st.header("📋 Dataset Overview")
    st.markdown("Review the structure, quality and contents of the uploaded dataset.")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Rows", f"{len(df):,}")
    with col2:
        st.metric("Columns", f"{len(df.columns):,}")
    with col3:
        st.metric("Missing Values", f"{int(df.isna().sum().sum()):,}")
    with col4:
        st.metric("Duplicate Rows", f"{int(df.duplicated().sum()):,}")

    st.subheader("Column Types")
    st.dataframe(
        pd.DataFrame(
            {
                "Column": df.columns,
                "Data Type": [str(dtype) for dtype in df.dtypes],
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Preview")
    st.dataframe(df.head(10), use_container_width=True)


def render_home():
    """Render the landing/home page for the dashboard."""
    st.header("🏠 Home")
    st.markdown(
        "Welcome to the Hotel Booking Analytics Dashboard. Upload a CSV dataset, prepare it, and use the sidebar to explore the available analysis views."
    )

    if st.session_state.get("cleaned_df") is not None:
        st.success("A prepared dataset is available and ready for analysis.")
    else:
        st.info("No prepared dataset is available yet. Upload a CSV file and run data preparation to get started.")


def render_global_filters(df):
    """Apply simple global filters for the dashboard."""
    if df is None or df.empty:
        return df

    filtered_df = df.copy()

    if "hotel" in filtered_df.columns and filtered_df["hotel"].notna().any():
        hotel_values = sorted({str(value) for value in filtered_df["hotel"].dropna().unique()})
        if len(hotel_values) > 1:
            selected_hotel = st.sidebar.selectbox(
                "Hotel",
                options=["All"] + hotel_values,
                key="global_hotel_filter",
            )
            if selected_hotel != "All":
                filtered_df = filtered_df[filtered_df["hotel"].astype(str) == selected_hotel]

    if "arrival_date_year" in filtered_df.columns and filtered_df["arrival_date_year"].notna().any():
        year_values = sorted({int(value) for value in filtered_df["arrival_date_year"].dropna().unique() if pd.notna(value)})
        if len(year_values) > 1:
            selected_year = st.sidebar.selectbox(
                "Year",
                options=["All"] + year_values,
                key="global_year_filter",
            )
            if selected_year != "All":
                filtered_df = filtered_df[filtered_df["arrival_date_year"] == selected_year]

    if "arrival_date_month" in filtered_df.columns and filtered_df["arrival_date_month"].notna().any():
        month_values = sorted({str(value) for value in filtered_df["arrival_date_month"].dropna().unique() if pd.notna(value)})
        if len(month_values) > 1:
            selected_month = st.sidebar.selectbox(
                "Month",
                options=["All"] + month_values,
                key="global_month_filter",
            )
            if selected_month != "All":
                filtered_df = filtered_df[filtered_df["arrival_date_month"].astype(str) == selected_month]

    return filtered_df


def render_market_channel_analysis(df):
    """Render market segment and distribution channel insights for the current dataset."""
    if df is None or df.empty:
        st.info("No data available for the market and channel analysis.")
        return

    data = df.copy()

    if "market_segment" in data.columns:
        data["market_segment"] = data["market_segment"].fillna("Unknown").astype(str).str.strip()
    else:
        data["market_segment"] = "Unknown"

    if "distribution_channel" in data.columns:
        data["distribution_channel"] = data["distribution_channel"].fillna("Unknown").astype(str).str.strip()
    else:
        data["distribution_channel"] = "Unknown"

    if "city" in data.columns:
        data["city"] = data["city"].fillna("Unknown").astype(str).str.strip()
    else:
        data["city"] = "Unknown"

    st.header("🌍 Market & Channel Analysis")
    st.markdown("Understand which market segments and distribution channels drive bookings and cancellations.")

    col1, col2 = st.columns(2)
    with col1:
        segment_counts = data["market_segment"].value_counts().reset_index()
        segment_counts.columns = ["market_segment", "bookings"]
        fig = px.bar(
            segment_counts.head(10),
            x="market_segment",
            y="bookings",
            color="market_segment",
            title="Bookings by Market Segment",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        channel_counts = data["distribution_channel"].value_counts().reset_index()
        channel_counts.columns = ["distribution_channel", "bookings"]
        fig = px.bar(
            channel_counts.head(10),
            x="distribution_channel",
            y="bookings",
            color="distribution_channel",
            title="Bookings by Distribution Channel",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Market Segment vs Distribution Channel")
    cross_tab = pd.crosstab(data["market_segment"], data["distribution_channel"])
    fig = px.imshow(
        cross_tab,
        labels={"x": "Distribution Channel", "y": "Market Segment", "color": "Bookings"},
        title="Distribution Channel Mix by Market Segment",
    )
    st.plotly_chart(fig, use_container_width=True)

    if "is_canceled" in data.columns:
        data["is_canceled"] = pd.to_numeric(data["is_canceled"], errors="coerce").fillna(0)
        cancellation_summary = (
            data.groupby(["market_segment", "distribution_channel"], dropna=False)["is_canceled"]
            .mean()
            .reset_index(name="cancellation_rate")
        )
        cancellation_summary["cancellation_rate"] = cancellation_summary["cancellation_rate"] * 100
        fig = px.scatter(
            cancellation_summary,
            x="market_segment",
            y="distribution_channel",
            size="cancellation_rate",
            color="cancellation_rate",
            title="Cancellation Rate by Market Segment and Channel",
        )
        st.plotly_chart(fig, use_container_width=True)


def render_executive_overview(df):
    """Render a lightweight executive overview for the current dataset."""
    if df is None or df.empty:
        st.info("No data available for the executive overview.")
        return

    data = df.copy()

    if "is_canceled" in data.columns:
        data["is_canceled"] = pd.to_numeric(data["is_canceled"], errors="coerce").fillna(0)

    if "adr" in data.columns:
        data["adr"] = pd.to_numeric(data["adr"], errors="coerce").fillna(0)

    if (
        "stays_in_weekend_nights" in data.columns
        and "stays_in_weekdays_nights" in data.columns
    ):
        data["total_stay_nights"] = (
            pd.to_numeric(data["stays_in_weekend_nights"], errors="coerce").fillna(0)
            + pd.to_numeric(data["stays_in_weekdays_nights"], errors="coerce").fillna(0)
        )
    else:
        data["total_stay_nights"] = 0

    if "adr" in data.columns and "total_stay_nights" in data.columns:
        data["estimated_revenue"] = data["adr"] * data["total_stay_nights"]
    else:
        data["estimated_revenue"] = 0.0

    total_bookings = len(data)
    cancellation_rate = (
        data["is_canceled"].mean() * 100 if "is_canceled" in data.columns else 0
    )
    total_revenue = (
        data["estimated_revenue"].sum() if "estimated_revenue" in data.columns else 0
    )
    avg_adr = data["adr"].mean() if "adr" in data.columns else 0

    st.markdown("""
    <div class="revenue-header">
        <div class="revenue-title">📊 Executive Overview</div>
        <div class="revenue-subtitle">High-level summary of booking volume, cancellations, revenue and demand patterns.</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Bookings", f"{total_bookings:,}")
    with col2:
        st.metric("Cancellation Rate", f"{cancellation_rate:.1f}%")
    with col3:
        st.metric("Estimated Revenue", f"{total_revenue:,.0f}")

    if "hotel" in data.columns and data["hotel"].notna().any():
        hotel_summary = data.groupby("hotel", dropna=False).size().reset_index(name="bookings")
        st.subheader("Bookings by Hotel")
        st.bar_chart(hotel_summary.set_index("hotel")["bookings"])

    if "arrival_date_month" in data.columns and data["arrival_date_month"].notna().any():
        monthly_summary = data.groupby("arrival_date_month", dropna=False).size().reset_index(name="bookings")
        st.subheader("Bookings by Month")
        st.bar_chart(monthly_summary.set_index("arrival_date_month")["bookings"])

# Main dashboard rendering is handled after the sidebar and page functions are defined.
#====================================================================================
# SIDEBAR SECTION
#====================================================================================

def render_sidebar(
    df=None,
    original_df=None,
    cleaning_stats=None
):
    """
    Creates the complete Hotel Analytics sidebar.

    Parameters
    ----------
    df : pandas.DataFrame
        Final/prepared dataset.

    original_df : pandas.DataFrame
        Dataset before preparation.

    cleaning_stats : dict
        Statistics generated during data preparation.
    """

    # --------------------------------------------------------
    # DEFAULT VALUES
    # --------------------------------------------------------

    if cleaning_stats is None:
        cleaning_stats = {}

    if original_df is not None and df is not None:
        if "duplicates_removed" not in cleaning_stats:
            duplicates_removed = int(original_df.duplicated().sum())
        else:
            duplicates_removed = int(cleaning_stats.get("duplicates_removed", 0))

        if "missing_values_fixed" not in cleaning_stats:
            missing_values_fixed = max(
                int(original_df.isna().sum().sum() - df.isna().sum().sum()),
                0,
            )
        else:
            missing_values_fixed = int(cleaning_stats.get("missing_values_fixed", 0))

        if "invalid_rows_removed" not in cleaning_stats:
            invalid_rows_removed = 0
        else:
            invalid_rows_removed = int(cleaning_stats.get("invalid_rows_removed", 0))

        if "outliers_removed" not in cleaning_stats:
            outliers_removed = 0
        else:
            outliers_removed = int(cleaning_stats.get("outliers_removed", 0))

        if "dtypes_fixed" not in cleaning_stats:
            dtypes_fixed = int(sum(
                1 for column in original_df.columns
                if column in df.columns and str(original_df[column].dtype) != str(df[column].dtype)
            ))
        else:
            dtypes_fixed = int(cleaning_stats.get("dtypes_fixed", 0))
    else:
        duplicates_removed = int(cleaning_stats.get("duplicates_removed", 0))
        missing_values_fixed = int(cleaning_stats.get("missing_values_fixed", 0))
        invalid_rows_removed = int(cleaning_stats.get("invalid_rows_removed", 0))
        outliers_removed = int(cleaning_stats.get("outliers_removed", 0))
        dtypes_fixed = int(cleaning_stats.get("dtypes_fixed", 0))

    # --------------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------------

    with st.sidebar:

        # ====================================================
        # BRAND / HEADER
        # ====================================================

        st.markdown("""
        <div class="sidebar-brand">

            <div class="sidebar-logo">
                🏨
            </div>

            <div class="sidebar-brand-title">
                Hotel Analytics
            </div>

            <div class="sidebar-brand-subtitle">
                Business Intelligence Dashboard
            </div>

        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            "<div class='sidebar-divider'></div>",
            unsafe_allow_html=True
        )

        # ====================================================
        # NAVIGATION
        # ====================================================

        st.markdown("""
        <div class="sidebar-section-title">
            NAVIGATION
        </div>
        """, unsafe_allow_html=True)

        pages = [
            "🏠 Home",
            "📋 Dataset Overview",
            "🧹 Data Preparation",

            "📊 Executive Overview",
            "🏨 Hotel Performance",
            "📅 Booking Trends",
            "❌ Cancellation Analysis",
            "⏳ Lead Time Analysis",
            "🛏️ Stay Duration",
            "💰 Revenue Analysis",
            "👥 Customer Analysis",
            "🌍 Market & Channel Analysis",
            "🔎 Relationship Analysis",

            "📌 Business Insights",
            "💡 Recommendations",

            "ℹ️ About"
        ]

        selected_page = st.selectbox(
            "Go to",
            pages,
            key="sidebar_navigation",
            label_visibility="collapsed"
        )

        st.markdown(
            "<div class='sidebar-divider'></div>",
            unsafe_allow_html=True
        )

        # ====================================================
        # DATASET STATUS
        # ====================================================

        st.markdown("""
        <div class="sidebar-section-title">
            DATASET STATUS
        </div>
        """, unsafe_allow_html=True)

        if df is not None and not df.empty:

            st.markdown("""
            <div class="dataset-status-card">

                <div class="status-dot"></div>

                <div>
                    <div class="status-title">
                        Dataset Ready
                    </div>

                    <div class="status-subtitle">
                        Prepared for analysis
                    </div>
                </div>

            </div>
            """, unsafe_allow_html=True)

        else:

            st.markdown("""
            <div class="dataset-status-card not-ready">

                <div class="status-dot"></div>

                <div>
                    <div class="status-title">
                        No Dataset
                    </div>

                    <div class="status-subtitle">
                        Upload a dataset to begin
                    </div>
                </div>

            </div>
            """, unsafe_allow_html=True)

        # ====================================================
        # DATASET INFORMATION
        # ====================================================

        if df is not None and not df.empty:

            st.markdown("""
            <div class="sidebar-section-title">
                DATASET INFORMATION
            </div>
            """, unsafe_allow_html=True)

            rows = len(df)
            columns = len(df.columns)

            missing_values = int(
                df.isna().sum().sum()
            )

            duplicate_rows = int(
                df.duplicated().sum()
            )

            # -----------------------------------------------
            # ROWS
            # -----------------------------------------------

            st.markdown(f"""
            <div class="sidebar-metric">

                <span>📊 Records</span>

                <strong>
                    {rows:,}
                </strong>

            </div>
            """, unsafe_allow_html=True)

            # -----------------------------------------------
            # COLUMNS
            # -----------------------------------------------

            st.markdown(f"""
            <div class="sidebar-metric">

                <span>📐 Columns</span>

                <strong>
                    {columns:,}
                </strong>

            </div>
            """, unsafe_allow_html=True)

            # -----------------------------------------------
            # MISSING VALUES
            # -----------------------------------------------

            missing_class = (
                "good"
                if missing_values == 0
                else "warning"
            )

            st.markdown(f"""
            <div class="sidebar-metric">

                <span>⚠️ Missing Values</span>

                <strong class="{missing_class}">
                    {missing_values:,}
                </strong>

            </div>
            """, unsafe_allow_html=True)

            # -----------------------------------------------
            # DUPLICATES
            # -----------------------------------------------

            duplicate_class = (
                "good"
                if duplicate_rows == 0
                else "warning"
            )

            st.markdown(f"""
            <div class="sidebar-metric">

                <span>♻️ Duplicate Rows</span>

                <strong class="{duplicate_class}">
                    {duplicate_rows:,}
                </strong>

            </div>
            """, unsafe_allow_html=True)

            # =================================================
            # PREPARATION SUMMARY
            # =================================================

            st.markdown("""
            <div class="sidebar-section-title">
                🧹 PREPARATION SUMMARY
            </div>
            """, unsafe_allow_html=True)

            # Original rows
            original_rows = cleaning_stats.get(
                "original_rows",
                len(original_df)
                if original_df is not None
                else len(df)
            )

            # Final rows
            final_rows = cleaning_stats.get(
                "final_rows",
                len(df)
            )

            # Duplicates removed
            duplicates_removed = cleaning_stats.get(
                "duplicates_removed",
                0
            )

            # Missing values fixed
            missing_fixed = cleaning_stats.get(
                "missing_values_fixed",
                0
            )

            # Invalid rows removed
            invalid_removed = cleaning_stats.get(
                "invalid_rows_removed",
                0
            )

            # Outliers removed
            outliers_removed = cleaning_stats.get(
                "outliers_removed",
                0
            )

            # Data types fixed
            dtypes_fixed = cleaning_stats.get(
                "dtypes_fixed",
                0
            )

            # -----------------------------------------------
            # PREPARATION PROGRESS
            # -----------------------------------------------

            preparation_steps = [
                (
                    "Missing Values",
                    missing_fixed
                ),
                (
                    "Duplicates",
                    duplicates_removed
                ),
                (
                    "Invalid Records",
                    invalid_removed
                ),
                (
                    "Outliers",
                    outliers_removed
                ),
                (
                    "Data Types",
                    dtypes_fixed
                )
            ]

            for step_name, step_value in preparation_steps:

                if step_value > 0:

                    st.markdown(f"""
                    <div class="cleaning-item">

                        <span>
                            ✓ {step_name}
                        </span>

                        <strong>
                            {step_value:,}
                        </strong>

                    </div>
                    """, unsafe_allow_html=True)

                else:

                    st.markdown(f"""
                    <div class="cleaning-item">

                        <span>
                            ✓ {step_name}
                        </span>

                        <strong class="zero">
                            0
                        </strong>

                    </div>
                    """, unsafe_allow_html=True)

            # =================================================
            # BEFORE → AFTER
            # =================================================

            st.markdown("""
            <div class="before-after-title">
                Dataset Transformation
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="transformation-box">

                <div class="transformation-item">

                    <span>
                        Original
                    </span>

                    <strong>
                        {original_rows:,}
                    </strong>

                </div>

                <div class="transformation-arrow">
                    ↓
                </div>

                <div class="transformation-item">

                    <span>
                        Prepared
                    </span>

                    <strong class="prepared-number">
                        {final_rows:,}
                    </strong>

                </div>

            </div>
            """, unsafe_allow_html=True)

            # =================================================
            # DATASET PREVIEW
            # =================================================

            st.markdown("""
            <div class="sidebar-section-title">
                👁️ DATASET PREVIEW
            </div>
            """, unsafe_allow_html=True)

            preview_rows = st.number_input(
                "Preview rows",
                min_value=3,
                max_value=10,
                value=5,
                step=1,
                key="sidebar_preview_rows"
            )

            with st.expander(
                "View prepared data",
                expanded=False
            ):

                st.dataframe(
                    df.head(preview_rows),
                    use_container_width=True,
                    height=250
                )

            # =================================================
            # COLUMN INFORMATION
            # =================================================

            with st.expander(
                "View columns",
                expanded=False
            ):

                for column in df.columns:

                    dtype = str(
                        df[column].dtype
                    )

                    st.markdown(f"""
                    <div class="column-item">

                        <span>
                            {column}
                        </span>

                        <small>
                            {dtype}
                        </small>

                    </div>
                    """, unsafe_allow_html=True)

            # =================================================
            # DOWNLOAD PREPARED DATASET
            # =================================================

            st.markdown("""
            <div class="sidebar-section-title">
                📥 EXPORT
            </div>
            """, unsafe_allow_html=True)

            csv_data = df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                label="⬇️ Download Prepared Dataset",
                data=csv_data,
                file_name="prepared_hotel_bookings.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_prepared_dataset"
            )

        # ====================================================
        # FOOTER
        # ====================================================

        st.markdown("""
        <div class="sidebar-footer">

            <div>
                Hotel Booking BI
            </div>

            <small>
                Python • Pandas • Plotly • Streamlit
            </small>

        </div>
        """, unsafe_allow_html=True)

    return selected_page

# Capture the sidebar navigation selection so downstream page rendering can use it.
cleaning_stats = st.session_state.get("cleaning_stats", {})
selected_page = render_sidebar(
    df=st.session_state.get("cleaned_df"),
    original_df=st.session_state.get("original_df"),
    cleaning_stats=cleaning_stats,
)

st.markdown("""
<style>

/* =========================================================
   SIDEBAR
   ========================================================= */

section[data-testid="stSidebar"] {

    background:
        linear-gradient(
            180deg,
            #0b0d0c 0%,
            #101412 50%,
            #0a0c0b 100%
        );

    border-right: 1px solid rgba(255,255,255,0.07);
}


/* =========================================================
   BRAND
   ========================================================= */

.sidebar-brand {

    padding: 10px 4px 18px 4px;

    text-align: left;
}

.sidebar-logo {

    font-size: 30px;

    margin-bottom: 5px;

    filter:
        drop-shadow(
            0 0 10px rgba(77,255,136,0.35)
        );
}

.sidebar-brand-title {

    font-size: 21px;

    font-weight: 800;

    color: #ffffff;

    letter-spacing: 0.2px;
}

.sidebar-brand-subtitle {

    margin-top: 4px;

    font-size: 11px;

    color: #8d9690;

    line-height: 1.4;
}


/* =========================================================
   DIVIDER
   ========================================================= */

.sidebar-divider {

    height: 1px;

    margin: 12px 0 18px 0;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(77,255,136,0.20),
            transparent
        );
}


/* =========================================================
   SECTION TITLES
   ========================================================= */

.sidebar-section-title {

    margin-top: 18px;

    margin-bottom: 9px;

    font-size: 10px;

    font-weight: 800;

    letter-spacing: 1.4px;

    color: #66716a;
}


/* =========================================================
   DATASET STATUS
   ========================================================= */

.dataset-status-card {

    display: flex;

    align-items: center;

    gap: 11px;

    padding: 12px;

    margin-bottom: 10px;

    border-radius: 10px;

    background:
        rgba(77,255,136,0.055);

    border:
        1px solid rgba(77,255,136,0.15);

    box-shadow:
        0 0 18px rgba(77,255,136,0.05);
}

.dataset-status-card.not-ready {

    background:
        rgba(255,255,255,0.025);

    border-color:
        rgba(255,255,255,0.08);
}

.status-dot {

    width: 9px;

    height: 9px;

    min-width: 9px;

    border-radius: 50%;

    background: #4dff88;

    box-shadow:
        0 0 10px rgba(77,255,136,0.8);
}

.not-ready .status-dot {

    background: #777;

    box-shadow: none;
}

.status-title {

    color: #ffffff;

    font-size: 13px;

    font-weight: 700;
}

.status-subtitle {

    color: #78827c;

    font-size: 10px;

    margin-top: 2px;
}


/* =========================================================
   SIDEBAR METRICS
   ========================================================= */

.sidebar-metric {

    display: flex;

    align-items: center;

    justify-content: space-between;

    padding: 8px 10px;

    margin-bottom: 5px;

    border-radius: 7px;

    background:
        rgba(255,255,255,0.025);
}

.sidebar-metric span {

    color: #a0aaa4;

    font-size: 11px;
}

.sidebar-metric strong {

    color: #ffffff;

    font-size: 12px;
}

.sidebar-metric strong.good {

    color: #4dff88;
}

.sidebar-metric strong.warning {

    color: #ffc857;
}


/* =========================================================
   CLEANING ITEMS
   ========================================================= */

.cleaning-item {

    display: flex;

    align-items: center;

    justify-content: space-between;

    padding: 7px 9px;

    margin-bottom: 4px;

    border-radius: 7px;

    background:
        rgba(255,255,255,0.025);

    color: #b3bbb6;

    font-size: 11px;
}

.cleaning-item strong {

    color: #4dff88;

    font-size: 11px;
}

.cleaning-item strong.zero {

    color: #66716a;
}


/* =========================================================
   BEFORE / AFTER
   ========================================================= */

.before-after-title {

    margin-top: 15px;

    margin-bottom: 8px;

    color: #8d9690;

    font-size: 10px;

    font-weight: 700;

    text-transform: uppercase;

    letter-spacing: 0.8px;
}

.transformation-box {

    padding: 12px;

    border-radius: 10px;

    background:
        rgba(255,255,255,0.025);

    border:
        1px solid rgba(255,255,255,0.06);

    text-align: center;
}

.transformation-item {

    display: flex;

    justify-content: space-between;

    align-items: center;

    color: #8d9690;

    font-size: 11px;
}

.transformation-item strong {

    color: #ffffff;

    font-size: 13px;
}

.transformation-item strong.prepared-number {

    color: #4dff88;
}

.transformation-arrow {

    padding: 4px;

    color: #4dff88;

    font-size: 16px;

    text-shadow:
        0 0 8px rgba(77,255,136,0.6);
}


/* =========================================================
   COLUMN LIST
   ========================================================= */

.column-item {

    display: flex;

    justify-content: space-between;

    align-items: center;

    gap: 8px;

    padding: 5px 0;

    border-bottom:
        1px solid rgba(255,255,255,0.04);

    color: #c4cbc6;

    font-size: 10px;
}

.column-item small {

    color: #657069;

    font-size: 9px;

    white-space: nowrap;
}


/* =========================================================
   SELECTBOX
   ========================================================= */

section[data-testid="stSidebar"]
div[data-baseweb="select"] > div {

    background:
        rgba(255,255,255,0.045) !important;

    border:
        1px solid rgba(255,255,255,0.10) !important;

    border-radius: 9px !important;

    min-height: 42px !important;
}

section[data-testid="stSidebar"]
div[data-baseweb="select"] > div:hover {

    border-color:
        rgba(77,255,136,0.45) !important;

    box-shadow:
        0 0 12px rgba(77,255,136,0.08);
}


/* =========================================================
   DOWNLOAD BUTTON
   ========================================================= */

section[data-testid="stSidebar"]
.stDownloadButton button {

    border-radius: 8px !important;

    border:
        1px solid rgba(77,255,136,0.25) !important;

    background:
        rgba(77,255,136,0.06) !important;

    color:
        #b9ffca !important;

    font-size: 11px !important;

    font-weight: 600 !important;

    transition:
        all 0.25s ease !important;
}

section[data-testid="stSidebar"]
.stDownloadButton button:hover {

    border-color:
        #4dff88 !important;

    color:
        #4dff88 !important;

    box-shadow:
        0 0 15px rgba(77,255,136,0.20) !important;
}


/* =========================================================
   FOOTER
   ========================================================= */

.sidebar-footer {

    margin-top: 25px;

    padding-top: 14px;

    border-top:
        1px solid rgba(255,255,255,0.06);

    color: #66716a;

    font-size: 10px;

    text-align: center;
}

.sidebar-footer small {

    display: block;

    margin-top: 4px;

    color: #4f5953;

    font-size: 8px;
}

</style>
""", unsafe_allow_html=True)


def render_hotel_performance(df):
    """Render a simple hotel performance analysis page."""

    if df is None or df.empty:
        st.warning("⚠️ No data available for hotel performance analysis.")
        return

    data = df.copy()

    st.markdown("""
    <div class="revenue-header">

        <div class="revenue-title">
            🏨 Hotel Performance
        </div>

        <div class="revenue-subtitle">
            Compare booking volume, cancellation behaviour and
            pricing strength across hotels in the selected data.
        </div>

    </div>
    """, unsafe_allow_html=True)

    if "hotel" not in data.columns:
        st.info("ℹ️ The current dataset does not contain a hotel column.")
        return

    hotel_summary = data.groupby("hotel", dropna=False).size().reset_index(name="bookings")

    if "is_canceled" in data.columns:
        hotel_summary["cancellation_rate"] = (
            data.groupby("hotel", dropna=False)["is_canceled"].mean().values
        )

    if "adr" in data.columns:
        hotel_summary["adr"] = (
            data.groupby("hotel", dropna=False)["adr"].mean().values
        )

    hotel_summary = hotel_summary.sort_values("bookings", ascending=False)

    if "cancellation_rate" in hotel_summary.columns:
        st.plotly_chart(
            px.bar(
                hotel_summary,
                x="hotel",
                y="cancellation_rate",
                color="hotel",
                title="Cancellation Rate by Hotel"
            ),
            use_container_width=True,
        )

    st.plotly_chart(
        px.bar(
            hotel_summary,
            x="hotel",
            y="bookings",
            color="hotel",
            title="Booking Volume by Hotel"
        ),
        use_container_width=True,
    )

    if "adr" in hotel_summary.columns:
        st.plotly_chart(
            px.bar(
                hotel_summary,
                x="hotel",
                y="adr",
                color="hotel",
                title="Average ADR by Hotel"
            ),
            use_container_width=True,
        )

    st.dataframe(hotel_summary, use_container_width=True)


# Derive preparation statistics when they were not explicitly provided.
duplicates_removed = (
    int(original_df.duplicated().sum())
    if original_df is not None
    else 0
)

missing_values_fixed = (
    max(int(original_df.isna().sum().sum() - df.isna().sum().sum()), 0)
    if original_df is not None and df is not None
    else 0
)

invalid_rows_removed = 0
outliers_removed = 0
dtypes_fixed = (
    int(
        sum(
            1
            for column in original_df.columns
            if column in df.columns and str(original_df[column].dtype) != str(df[column].dtype)
        )
    )
    if original_df is not None and df is not None
    else 0
)

cleaning_stats = {

    "original_rows": len(original_df),

    "final_rows": len(df),

    "duplicates_removed": duplicates_removed,

    "missing_values_fixed": missing_values_fixed,

    "invalid_rows_removed": invalid_rows_removed,

    "outliers_removed": outliers_removed,

    "dtypes_fixed": dtypes_fixed

}

def render_booking_trends(df):
    """Render booking trend insights for the prepared dataset."""
    st.header("📅 Booking Trends")

    if df is None or df.empty:
        st.info("No data available to display booking trends.")
        return

    required_columns = ["arrival_date_year", "arrival_date_month"]
    missing_columns = [column for column in required_columns if column not in df.columns]

    if missing_columns:
        st.warning(f"Required columns missing for booking trends: {', '.join(missing_columns)}")
        return

    trend_df = (
        df.groupby(["arrival_date_year", "arrival_date_month"], as_index=False)
        .size()
        .rename(columns={"size": "bookings"})
    )

    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    trend_df["arrival_date_month"] = pd.Categorical(
        trend_df["arrival_date_month"],
        categories=month_order,
        ordered=True,
    )
    trend_df = trend_df.sort_values(["arrival_date_year", "arrival_date_month"]).dropna()

    st.subheader("Booking Volume by Month")
    fig = px.line(
        trend_df,
        x="arrival_date_month",
        y="bookings",
        color="arrival_date_year",
        markers=True,
        title="Bookings by Month",
    )
    st.plotly_chart(fig, use_container_width=True)

    if "is_canceled" in df.columns:
        cancellation_df = (
            df.groupby(["arrival_date_year", "arrival_date_month", "is_canceled"], as_index=False)
            .size()
            .rename(columns={"size": "count"})
        )
        cancellation_df["status"] = np.where(cancellation_df["is_canceled"] == 1, "Canceled", "Not Canceled")
        cancellation_df["arrival_date_month"] = pd.Categorical(
            cancellation_df["arrival_date_month"],
            categories=month_order,
            ordered=True,
        )
        cancellation_df = cancellation_df.sort_values(["arrival_date_year", "arrival_date_month"]).dropna()

        st.subheader("Cancellation Pattern by Month")
        cancellation_fig = px.bar(
            cancellation_df,
            x="arrival_date_month",
            y="count",
            color="status",
            barmode="group",
            title="Canceled vs. Non-Canceled Bookings by Month",
        )
        st.plotly_chart(cancellation_fig, use_container_width=True)


def render_cancellation_analysis(df):
    """Render cancellation analysis for the prepared dataset."""
    st.header("❌ Cancellation Analysis")

    if df is None or df.empty:
        st.info("No data available to display cancellation analysis.")
        return

    if "is_canceled" not in df.columns:
        st.warning("Required column missing for cancellation analysis: is_canceled")
        return

    analysis_df = df.copy()
    analysis_df["is_canceled"] = pd.to_numeric(
        analysis_df["is_canceled"], errors="coerce"
    ).fillna(0)

    cancellation_rate = analysis_df["is_canceled"].mean() * 100

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Cancellation Rate", f"{cancellation_rate:.1f}%")
    with col2:
        st.metric("Canceled Bookings", f"{int(analysis_df['is_canceled'].sum()):,}")

    if "hotel" in analysis_df.columns:
        hotel_summary = (
            analysis_df.groupby("hotel", dropna=False)["is_canceled"]
            .mean()
            .reset_index(name="cancellation_rate")
            .sort_values("cancellation_rate", ascending=False)
        )
        st.subheader("Cancellation Rate by Hotel")
        st.plotly_chart(
            px.bar(
                hotel_summary,
                x="hotel",
                y="cancellation_rate",
                title="Cancellation Rate by Hotel",
            ),
            use_container_width=True,
        )

    if "market_segment" in analysis_df.columns:
        market_summary = (
            analysis_df.groupby("market_segment", dropna=False)["is_canceled"]
            .mean()
            .reset_index(name="cancellation_rate")
            .sort_values("cancellation_rate", ascending=False)
        )
        st.subheader("Cancellation Rate by Market Segment")
        st.plotly_chart(
            px.bar(
                market_summary,
                x="market_segment",
                y="cancellation_rate",
                title="Cancellation Rate by Market Segment",
            ),
            use_container_width=True,
        )


def render_lead_time_analysis(df):
    """Render a simple lead time analysis view."""
    st.header("⏳ Lead Time Analysis")

    if "lead_time" not in df.columns:
        st.info("The dataset does not contain a 'lead_time' column.")
        return

    analysis_df = df.copy()
    analysis_df["lead_time_num"] = pd.to_numeric(analysis_df["lead_time"], errors="coerce")

    bins = [0, 7, 30, 90, 180, 365, np.inf]
    labels = ["0-7 days", "8-30 days", "31-90 days", "91-180 days", "181-365 days", "365+ days"]
    analysis_df["lead_time_bucket"] = pd.cut(
        analysis_df["lead_time_num"],
        bins=bins,
        labels=labels,
        include_lowest=True,
    )

    distribution = (
        analysis_df.groupby("lead_time_bucket", dropna=False)
        .size()
        .reset_index(name="bookings")
    )

    st.subheader("Lead Time Distribution")
    st.plotly_chart(
        px.bar(
            distribution,
            x="lead_time_bucket",
            y="bookings",
            title="Lead Time Distribution",
        ),
        use_container_width=True,
    )

    if "is_canceled" in analysis_df.columns:
        cancellation_summary = (
            analysis_df.groupby("lead_time_bucket", dropna=False)["is_canceled"]
            .mean()
            .reset_index(name="cancellation_rate")
        )
        st.subheader("Cancellation Rate by Lead Time")
        st.plotly_chart(
            px.bar(
                cancellation_summary,
                x="lead_time_bucket",
                y="cancellation_rate",
                title="Cancellation Rate by Lead Time",
            ),
            use_container_width=True,
        )


def render_correlation_analysis(df):
    """Render a simple correlation analysis for numeric columns."""
    st.header("🔎 Relationship Analysis")

    if df is None or df.empty:
        st.info("No data available to display relationship analysis.")
        return

    numeric_df = df.select_dtypes(include=["number"]).copy()

    if numeric_df.shape[1] < 2:
        st.info("Not enough numeric columns for correlation analysis.")
        return

    corr_matrix = numeric_df.corr()

    st.subheader("Correlation Heatmap")
    st.plotly_chart(
        px.imshow(
            corr_matrix,
            title="Correlation Matrix",
            color_continuous_scale="Viridis",
            text_auto=False,
        ),
        use_container_width=True,
    )

    if "is_canceled" in corr_matrix.columns:
        st.subheader("Correlation with Cancellation")
        correlation_with_cancellation = (
            corr_matrix["is_canceled"]
            .drop("is_canceled")
            .sort_values(ascending=False)
        )
        st.dataframe(
            correlation_with_cancellation.rename("correlation"),
            use_container_width=True,
        )


def render_business_insights(df):
    """Render simple business insights for the prepared dataset."""
    st.header("📌 Business Insights")

    if df is None or df.empty:
        st.info("No data available to display business insights.")
        return

    insights = []

    if "is_canceled" in df.columns:
        cancellation_rate = df["is_canceled"].mean() * 100
        insights.append(f"Cancellation rate is {cancellation_rate:.1f}%.")

    if "adr" in df.columns:
        avg_adr = df["adr"].mean()
        insights.append(f"Average ADR is {avg_adr:,.2f}.")

    if "hotel" in df.columns and "is_canceled" in df.columns:
        hotel_cancellation = (
            df.groupby("hotel", dropna=False)["is_canceled"]
            .mean()
            .reset_index(name="cancellation_rate")
            .sort_values("cancellation_rate", ascending=False)
        )
        top_hotel = hotel_cancellation.iloc[0]["hotel"] if not hotel_cancellation.empty else None
        if top_hotel is not None:
            insights.append(f"{top_hotel} has the highest cancellation rate.")

    if insights:
        for insight in insights:
            st.write(f"- {insight}")
    else:
        st.info("Not enough data to generate business insights.")


def render_recommendations(df):
    """Render simple recommendations for the prepared dataset."""
    st.header("💡 Recommendations")

    if df is None or df.empty:
        st.info("No data available to generate recommendations.")
        return

    recommendations = []

    if "is_canceled" in df.columns:
        cancellation_rate = df["is_canceled"].mean() * 100
        if cancellation_rate > 20:
            recommendations.append(
                "Review cancellation policies and reminder campaigns to reduce cancellations."
            )

    if "adr" in df.columns:
        if df["adr"].mean() < 100:
            recommendations.append("Explore pricing optimization to improve revenue per booking.")

    if recommendations:
        for recommendation in recommendations:
            st.write(f"- {recommendation}")
    else:
        st.info("No immediate recommendations based on the current snapshot.")


def render_about():
    """Render the About page content."""
    st.header("ℹ️ About")
    st.markdown(
        """
        This dashboard provides an interactive analysis of hotel booking data,
        including booking trends, cancellation behavior, revenue performance,
        and customer insights.

        It is designed to help stakeholders explore the data and identify
        actionable business opportunities.
        """
    )


def render_stay_duration_analysis(df):
    """Render stay duration analysis for the prepared dataset."""
    st.header("🛏️ Stay Duration Analysis")

    if df is None or df.empty:
        st.info("No data available to generate stay duration analysis.")
        return

    data = df.copy()

    if "total_stay_nights" not in data.columns:
        if (
            "stays_in_weekend_nights" in data.columns
            and "stays_in_weekdays_nights" in data.columns
        ):
            data["total_stay_nights"] = (
                pd.to_numeric(
                    data["stays_in_weekend_nights"],
                    errors="coerce"
                ).fillna(0)
                +
                pd.to_numeric(
                    data["stays_in_weekdays_nights"],
                    errors="coerce"
                ).fillna(0)
            )
        else:
            st.warning("⚠️ Stay duration information is not available in the dataset.")
            return

    data["total_stay_nights"] = pd.to_numeric(
        data["total_stay_nights"],
        errors="coerce"
    ).fillna(0)

    avg_stay = data["total_stay_nights"].mean()
    median_stay = data["total_stay_nights"].median()
    max_stay = data["total_stay_nights"].max()

    col1, col2, col3 = st.columns(3)
    col1.metric("Average Stay", f"{avg_stay:.1f} nights")
    col2.metric("Median Stay", f"{median_stay:.1f} nights")
    col3.metric("Longest Stay", f"{max_stay:.0f} nights")

    stay_distribution = (
        data["total_stay_nights"]
        .value_counts()
        .sort_index()
        .reset_index()
    )
    stay_distribution.columns = ["stay_length", "bookings"]

    fig = px.bar(
        stay_distribution,
        x="stay_length",
        y="bookings",
        text="bookings"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=400,
        xaxis_title="Stay Length (Nights)",
        yaxis_title="Bookings",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )
    st.plotly_chart(fig, use_container_width=True)

    if "hotel" in data.columns:
        hotel_stay = (
            data.groupby("hotel", dropna=False)["total_stay_nights"]
            .mean()
            .reset_index()
            .sort_values("total_stay_nights", ascending=False)
        )

        fig_hotel = px.bar(
            hotel_stay,
            x="hotel",
            y="total_stay_nights",
            text="total_stay_nights"
        )
        fig_hotel.update_traces(textposition="outside")
        fig_hotel.update_layout(
            height=400,
            xaxis_title="Hotel",
            yaxis_title="Average Stay (Nights)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        st.plotly_chart(fig_hotel, use_container_width=True)


def render_revenue_analysis(df):
    """Render a simple revenue analysis view."""
    st.header("💰 Revenue Analysis")

    if df is None or df.empty:
        st.info("No data available to display revenue analysis.")
        return

    analysis_df = df.copy()
    metrics = []

    if "adr" in analysis_df.columns:
        adr_series = pd.to_numeric(analysis_df["adr"], errors="coerce").fillna(0)
        metrics.append(("Average ADR", f"{adr_series.mean():,.2f}"))
        metrics.append(("Total ADR", f"{adr_series.sum():,.2f}"))

    if metrics:
        cols = st.columns(len(metrics))
        for col, (label, value) in zip(cols, metrics):
            col.metric(label, value)

    if "hotel" in analysis_df.columns and "adr" in analysis_df.columns:
        revenue_by_hotel = (
            analysis_df.assign(
                adr_value=pd.to_numeric(analysis_df["adr"], errors="coerce").fillna(0)
            )
            .groupby("hotel", dropna=False)["adr_value"]
            .sum()
            .reset_index(name="revenue")
            .sort_values("revenue", ascending=False)
        )
        st.subheader("Revenue by Hotel")
        st.plotly_chart(
            px.bar(
                revenue_by_hotel,
                x="hotel",
                y="revenue",
                title="Revenue by Hotel",
            ),
            use_container_width=True,
        )

    if "adr" not in analysis_df.columns:
        st.info("No revenue-related columns are available in the dataset.")


def render_customer_analysis(df):
    """Render a simple customer analysis view."""
    st.header("👥 Customer Analysis")

    if df is None or df.empty:
        st.info("No data available to display customer analysis.")
        return

    analysis_df = df.copy()

    metrics = []
    if "is_repeated_guest" in analysis_df.columns:
        repeated_guest_rate = (
            pd.to_numeric(analysis_df["is_repeated_guest"], errors="coerce")
            .fillna(0)
            .mean()
            * 100
        )
        metrics.append(("Repeated Guest Rate", f"{repeated_guest_rate:.1f}%"))

    if "customer_type" in analysis_df.columns:
        customer_summary = (
            analysis_df.groupby("customer_type", dropna=False)
            .size()
            .reset_index(name="bookings")
            .sort_values("bookings", ascending=False)
        )
        st.subheader("Bookings by Customer Type")
        st.plotly_chart(
            px.bar(
                customer_summary,
                x="customer_type",
                y="bookings",
                title="Bookings by Customer Type",
            ),
            use_container_width=True,
        )

    if metrics:
        cols = st.columns(len(metrics))
        for col, (label, value) in zip(cols, metrics):
            col.metric(label, value)

    if not metrics and "customer_type" not in analysis_df.columns:
        st.info("No customer-related columns are available in the dataset.")


def render_market_channel_analysis(df):
    """Render a simple market and channel analysis view."""
    st.header("🌍 Market & Channel Analysis")

    if df is None or df.empty:
        st.info("No data available to display market and channel analysis.")
        return

    analysis_df = df.copy()
    plotted_anything = False

    for column in ["market_segment", "distribution_channel"]:
        if column in analysis_df.columns:
            summary = (
                analysis_df.groupby(column, dropna=False)
                .size()
                .reset_index(name="bookings")
                .sort_values("bookings", ascending=False)
            )
            st.subheader(f"Bookings by {column.replace('_', ' ').title()}")
            st.plotly_chart(
                px.bar(
                    summary,
                    x=column,
                    y="bookings",
                    title=f"Bookings by {column.replace('_', ' ').title()}",
                ),
                use_container_width=True,
            )
            plotted_anything = True

    if not plotted_anything:
        st.info("No market or channel columns are available in the dataset.")


filtered_df = df

if selected_page == "🏠 Home":

    render_home()


elif selected_page == "📋 Dataset Overview":

    render_dataset_overview(df)


elif selected_page == "🧹 Data Preparation":

    render_data_preparation(
        df,
        original_df,
        cleaning_stats
    )


elif selected_page == "📊 Executive Overview":

    render_executive_overview(filtered_df)


elif selected_page == "🏨 Hotel Performance":

    render_hotel_performance(filtered_df)


elif selected_page == "📅 Booking Trends":

    render_booking_trends(filtered_df)


elif selected_page == "❌ Cancellation Analysis":

    render_cancellation_analysis(filtered_df)


elif selected_page == "⏳ Lead Time Analysis":

    render_lead_time_analysis(filtered_df)


elif selected_page == "🛏️ Stay Duration":

    render_stay_duration_analysis(filtered_df)


elif selected_page == "💰 Revenue Analysis":

    render_revenue_analysis(filtered_df)


elif selected_page == "👥 Customer Analysis":

    render_customer_analysis(filtered_df)


elif selected_page == "🌍 Market & Channel Analysis":

    render_market_channel_analysis(filtered_df)


elif selected_page == "🔎 Relationship Analysis":

    render_correlation_analysis(filtered_df)


elif selected_page == "📌 Business Insights":

    render_business_insights(filtered_df)


elif selected_page == "💡 Recommendations":

    render_recommendations(filtered_df)


elif selected_page == "ℹ️ About":

    render_about()

#====================================================================================
# FILTER SECTION
#====================================================================================

# ============================================================
# 🎛️ GLOBAL DASHBOARD FILTERS
# ============================================================

def render_global_filters(df):

    if df is None or df.empty:
        st.warning("⚠️ No dataset available for filtering.")
        return df

    filtered_df = df.copy()

    # --------------------------------------------------------
    # CREATE DERIVED COLUMNS IF NOT ALREADY AVAILABLE
    # --------------------------------------------------------

    # Total Stay Nights
    if (
        "stays_in_weekend_nights" in filtered_df.columns
        and "stays_in_weekdays_nights" in filtered_df.columns
    ):

        if "total_stay_nights" not in filtered_df.columns:

            filtered_df["total_stay_nights"] = (
                pd.to_numeric(
                    filtered_df["stays_in_weekend_nights"],
                    errors="coerce"
                ).fillna(0)
                +
                pd.to_numeric(
                    filtered_df["stays_in_weekdays_nights"],
                    errors="coerce"
                ).fillna(0)
            )

    # Estimated Revenue
    if (
        "adr" in filtered_df.columns
        and "total_stay_nights" in filtered_df.columns
    ):

        if "estimated_revenue" not in filtered_df.columns:

            filtered_df["estimated_revenue"] = (
                pd.to_numeric(
                    filtered_df["adr"],
                    errors="coerce"
                ).fillna(0)
                *
                filtered_df["total_stay_nights"]
            )

    # --------------------------------------------------------
    # FILTER BOX HEADER
    # --------------------------------------------------------

    st.markdown("""
        <div class="global-filter-box">

            <div class="filter-heading">
                🎛️ Dashboard Filters
            </div>

            <div class="filter-subheading">
                Refine the analysis across all dashboard pages
            </div>

        </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # ROW 1
    # ========================================================

    col1, col2, col3 = st.columns(3)

    # --------------------------------------------------------
    # HOTEL
    # --------------------------------------------------------

    with col1:

        if "hotel" in filtered_df.columns:

            hotel_options = sorted(
                filtered_df["hotel"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            selected_hotels = st.multiselect(
                "🏨 Hotel",
                hotel_options,
                default=hotel_options,
                key="filter_hotel"
            )

            if selected_hotels:

                filtered_df = filtered_df[
                    filtered_df["hotel"]
                    .astype(str)
                    .isin(selected_hotels)
                ]

    # --------------------------------------------------------
    # YEAR
    # --------------------------------------------------------

    with col2:

        if "arrival_date_year" in filtered_df.columns:

            year_values = pd.to_numeric(
                filtered_df["arrival_date_year"],
                errors="coerce"
            ).dropna().unique()

            year_options = sorted(
                year_values.astype(int).tolist()
            )

            selected_years = st.multiselect(
                "📅 Year",
                year_options,
                default=year_options,
                key="filter_year"
            )

            if selected_years:

                filtered_df = filtered_df[
                    pd.to_numeric(
                        filtered_df["arrival_date_year"],
                        errors="coerce"
                    ).isin(selected_years)
                ]

    # --------------------------------------------------------
    # MONTH
    # --------------------------------------------------------

    with col3:

        if "arrival_date_month" in filtered_df.columns:

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

            available_months = (
                filtered_df["arrival_date_month"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            month_options = [
                month for month in month_order
                if month in available_months
            ]

            # Handle datasets containing abbreviated months
            if not month_options:
                month_options = sorted(available_months)

            selected_months = st.multiselect(
                "📆 Arrival Month",
                month_options,
                default=month_options,
                key="filter_month"
            )

            if selected_months:

                filtered_df = filtered_df[
                    filtered_df["arrival_date_month"]
                    .astype(str)
                    .isin(selected_months)
                ]

    # ========================================================
    # ROW 2
    # ========================================================

    col4, col5, col6 = st.columns(3)

    # --------------------------------------------------------
    # MARKET SEGMENT
    # --------------------------------------------------------

    with col4:

        if "market_segment" in filtered_df.columns:

            options = sorted(
                filtered_df["market_segment"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            selected_market = st.multiselect(
                "📊 Market Segment",
                options,
                default=options,
                key="filter_market_segment"
            )

            if selected_market:

                filtered_df = filtered_df[
                    filtered_df["market_segment"]
                    .astype(str)
                    .isin(selected_market)
                ]

    # --------------------------------------------------------
    # DISTRIBUTION CHANNEL
    # --------------------------------------------------------

    with col5:

        if "distribution_channel" in filtered_df.columns:

            options = sorted(
                filtered_df["distribution_channel"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            selected_channel = st.multiselect(
                "📢 Distribution Channel",
                options,
                default=options,
                key="filter_distribution_channel"
            )

            if selected_channel:

                filtered_df = filtered_df[
                    filtered_df["distribution_channel"]
                    .astype(str)
                    .isin(selected_channel)
                ]

    # --------------------------------------------------------
    # CUSTOMER TYPE
    # --------------------------------------------------------

    with col6:

        if "customer_type" in filtered_df.columns:

            options = sorted(
                filtered_df["customer_type"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            selected_customer = st.multiselect(
                "👥 Customer Type",
                options,
                default=options,
                key="filter_customer_type"
            )

            if selected_customer:

                filtered_df = filtered_df[
                    filtered_df["customer_type"]
                    .astype(str)
                    .isin(selected_customer)
                ]

    # ========================================================
    # ROW 3
    # ========================================================

    col7, col8, col9 = st.columns(3)

    # --------------------------------------------------------
    # DEPOSIT TYPE
    # --------------------------------------------------------

    with col7:

        if "deposit_type" in filtered_df.columns:

            options = sorted(
                filtered_df["deposit_type"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            selected_deposit = st.multiselect(
                "💳 Deposit Type",
                options,
                default=options,
                key="filter_deposit_type"
            )

            if selected_deposit:

                filtered_df = filtered_df[
                    filtered_df["deposit_type"]
                    .astype(str)
                    .isin(selected_deposit)
                ]

    # --------------------------------------------------------
    # MEAL
    # --------------------------------------------------------

    with col8:

        if "meal" in filtered_df.columns:

            options = sorted(
                filtered_df["meal"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            selected_meals = st.multiselect(
                "🍽️ Meal",
                options,
                default=options,
                key="filter_meal"
            )

            if selected_meals:

                filtered_df = filtered_df[
                    filtered_df["meal"]
                    .astype(str)
                    .isin(selected_meals)
                ]

    # --------------------------------------------------------
    # REPEAT GUEST
    # --------------------------------------------------------

    with col9:

        if "is_repeated_guest" in filtered_df.columns:

            repeat_options = {
                "New Guests": 0,
                "Repeat Guests": 1
            }

            selected_repeat = st.multiselect(
                "🔁 Guest Type",
                list(repeat_options.keys()),
                default=list(repeat_options.keys()),
                key="filter_repeat_guest"
            )

            selected_repeat_values = [
                repeat_options[item]
                for item in selected_repeat
            ]

            if selected_repeat_values:

                filtered_df = filtered_df[
                    filtered_df["is_repeated_guest"]
                    .isin(selected_repeat_values)
                ]

    # ========================================================
    # NUMERICAL RANGE FILTERS
    # ========================================================

    st.markdown("""
        <div class="range-filter-title">
            📐 Advanced Filters
        </div>
    """, unsafe_allow_html=True)

    col10, col11, col12 = st.columns(3)

    # --------------------------------------------------------
    # LEAD TIME
    # --------------------------------------------------------

    with col10:

        if "lead_time" in filtered_df.columns:

            lead_values = pd.to_numeric(
                filtered_df["lead_time"],
                errors="coerce"
            ).dropna()

            if not lead_values.empty:

                lead_min = int(lead_values.min())
                lead_max = int(lead_values.max())

                lead_range = st.slider(
                    "⏳ Lead Time (days)",
                    min_value=lead_min,
                    max_value=lead_max,
                    value=(lead_min, lead_max),
                    key="filter_lead_time"
                )

                filtered_df = filtered_df[
                    filtered_df["lead_time"].between(
                        lead_range[0],
                        lead_range[1]
                    )
                ]

    # --------------------------------------------------------
    # ADR
    # --------------------------------------------------------

    with col11:

        if "adr" in filtered_df.columns:

            adr_values = pd.to_numeric(
                filtered_df["adr"],
                errors="coerce"
            ).dropna()

            if not adr_values.empty:

                adr_min = float(adr_values.min())
                adr_max = float(adr_values.max())

                adr_range = st.slider(
                    "💰 ADR Range",
                    min_value=adr_min,
                    max_value=adr_max,
                    value=(adr_min, adr_max),
                    step=1.0,
                    key="filter_adr"
                )

                filtered_df = filtered_df[
                    filtered_df["adr"].between(
                        adr_range[0],
                        adr_range[1]
                    )
                ]

    # --------------------------------------------------------
    # STAY DURATION
    # --------------------------------------------------------

    with col12:

        if "total_stay_nights" in filtered_df.columns:

            stay_values = pd.to_numeric(
                filtered_df["total_stay_nights"],
                errors="coerce"
            ).dropna()

            if not stay_values.empty:

                stay_min = int(stay_values.min())
                stay_max = int(stay_values.max())

                stay_range = st.slider(
                    "🛏️ Stay Duration",
                    min_value=stay_min,
                    max_value=stay_max,
                    value=(stay_min, stay_max),
                    key="filter_stay_duration"
                )

                filtered_df = filtered_df[
                    filtered_df["total_stay_nights"].between(
                        stay_range[0],
                        stay_range[1]
                    )
                ]

    # ========================================================
    # FILTER STATUS
    # ========================================================

    st.markdown("<br>", unsafe_allow_html=True)

    status_col1, status_col2, status_col3 = st.columns(
        [1, 2, 1]
    )

    with status_col2:

        st.markdown(f"""
            <div class="filter-status">

                <span class="filter-status-icon">
                    🔎
                </span>

                <span>
                    Showing
                    <strong>{len(filtered_df):,}</strong>
                    of
                    <strong>{len(df):,}</strong>
                    bookings
                </span>

            </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # RESET FILTERS
    # ========================================================

    st.markdown("<br>", unsafe_allow_html=True)

    reset_col1, reset_col2, reset_col3 = st.columns(
        [1, 1, 1]
    )

    with reset_col2:

        if st.button(
            "🔄 Reset All Filters",
            use_container_width=True,
            key="reset_all_filters"
        ):

            filter_keys = [
                "filter_hotel",
                "filter_year",
                "filter_month",
                "filter_market_segment",
                "filter_distribution_channel",
                "filter_customer_type",
                "filter_deposit_type",
                "filter_meal",
                "filter_repeat_guest",
                "filter_lead_time",
                "filter_adr",
                "filter_stay_duration"
            ]

            for key in filter_keys:

                if key in st.session_state:
                    del st.session_state[key]

            st.rerun()

    return filtered_df

st.markdown("""
<style>

/* =========================================================
   GLOBAL FILTER BOX
   ========================================================= */

.global-filter-box {

    padding: 22px 26px;

    margin-top: 10px;
    margin-bottom: 20px;

    border-radius: 16px;

    background:
        linear-gradient(
            135deg,
            rgba(25,25,25,0.95),
            rgba(12,12,12,0.92)
        );

    border: 1px solid rgba(255,255,255,0.10);

    box-shadow:
        0 0 25px rgba(0,255,120,0.07),
        inset 0 0 20px rgba(255,255,255,0.015);
}


.filter-heading {

    color: white;

    font-size: 22px;

    font-weight: 800;

    letter-spacing: 0.3px;

}


.filter-subheading {

    color: #9a9a9a;

    font-size: 13px;

    margin-top: 5px;

}


/* =========================================================
   ADVANCED FILTER TITLE
   ========================================================= */

.range-filter-title {

    margin-top: 20px;
    margin-bottom: 12px;

    font-size: 16px;

    font-weight: 700;

    color: #ffffff;

}


/* =========================================================
   FILTER STATUS
   ========================================================= */

.filter-status {

    display: flex;

    align-items: center;

    justify-content: center;

    gap: 10px;

    padding: 10px 18px;

    border-radius: 10px;

    background: rgba(0,255,120,0.06);

    border: 1px solid rgba(0,255,120,0.18);

    color: #b7ffc9;

    font-size: 13px;

    box-shadow:
        0 0 15px rgba(0,255,120,0.08);

}


.filter-status strong {

    color: #4dff88;

}


/* =========================================================
   STREAMLIT MULTISELECT
   ========================================================= */

div[data-baseweb="select"] > div {

    border-radius: 9px !important;

}


/* =========================================================
   SLIDER
   ========================================================= */

div[data-testid="stSlider"] {

    padding-top: 5px;

}


/* =========================================================
   RESET BUTTON
   ========================================================= */

button[kind="secondary"] {

    border-radius: 9px !important;

    transition: all 0.25s ease !important;

}


button[kind="secondary"]:hover {

    border-color: #4dff88 !important;

    color: #4dff88 !important;

    box-shadow:
        0 0 15px rgba(77,255,136,0.25) !important;

}

</style>
""", unsafe_allow_html=True)


def render_business_insights(filtered_df):

    st.info(
        "📌 Business insights will be generated based on the selected filters."
    )


def render_stay_duration_analysis(filtered_df):

    st.info(
        "🛏️ Stay duration analysis is not available yet for the selected dataset."
    )


def render_recommendations(filtered_df):

    st.info(
        "💡 Recommendations will be generated based on the selected filters."
    )


if selected_page == "📊 Executive Overview":

    render_executive_overview(filtered_df)


elif selected_page == "🏨 Hotel Performance":

    render_hotel_performance(filtered_df)


elif selected_page == "📅 Booking Trends":

    render_booking_trends(filtered_df)


elif selected_page == "❌ Cancellation Analysis":

    render_cancellation_analysis(filtered_df)


elif selected_page == "⏳ Lead Time Analysis":

    render_lead_time_analysis(filtered_df)


elif selected_page == "🛏️ Stay Duration":

    render_stay_duration_analysis(filtered_df)


elif selected_page == "💰 Revenue Analysis":

    render_revenue_analysis(filtered_df)


elif selected_page == "🌍 Market & Channel Analysis":

    render_market_channel_analysis(filtered_df)


elif selected_page == "👥 Customer Analysis":

    render_customer_analysis(filtered_df)


elif selected_page == "📌 Business Insights":

    render_business_insights(filtered_df)


elif selected_page == "💡 Recommendations":

    render_recommendations(filtered_df)

#====================================================================================
# ANALYSIS SECTION
#====================================================================================

# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

def render_executive_overview(filtered_df):

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    if filtered_df is None or filtered_df.empty:

        st.warning(
            "⚠️ No booking records match the selected filters."
        )

        return

    # --------------------------------------------------------
    # EXECUTIVE OVERVIEW CSS
    # --------------------------------------------------------

    st.markdown("""
    <style>

    /* ======================================================
       EXECUTIVE OVERVIEW
       ====================================================== */

    .executive-header {
        margin-bottom: 22px;
    }

    .executive-title {
        font-size: 30px;
        font-weight: 700;
        color: white;
        margin-bottom: 4px;
    }

    .executive-subtitle {
        font-size: 14px;
        color: #a8a8a8;
        margin-bottom: 20px;
    }

    /* ======================================================
       KPI CARDS
       ====================================================== */

    .kpi-card {
        background: rgba(20, 20, 20, 0.90);
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-radius: 14px;
        padding: 18px 18px 16px 18px;
        min-height: 105px;
        margin-bottom: 14px;

        box-shadow:
            0 6px 22px rgba(0, 0, 0, 0.28),
            inset 0 0 20px rgba(255, 255, 255, 0.015);

        transition: all 0.25s ease;
    }

    .kpi-card:hover {
        transform: translateY(-2px);

        border-color: rgba(32, 255, 138, 0.35);

        box-shadow:
            0 8px 28px rgba(0, 0, 0, 0.35),
            0 0 18px rgba(32, 255, 138, 0.08);
    }

    .kpi-label {
        color: #a8a8a8;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 8px;
        letter-spacing: 0.2px;
    }

    .kpi-value {
        color: white;
        font-size: 25px;
        font-weight: 700;
        line-height: 1.1;
    }

    .kpi-icon {
        font-size: 17px;
        margin-right: 5px;
    }

    /* ======================================================
       SECTION HEADERS
       ====================================================== */

    .section-header {
        color: white;
        font-size: 19px;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 4px;
    }

    .section-description {
        color: #909090;
        font-size: 13px;
        margin-bottom: 12px;
    }

    /* ======================================================
       INSIGHT CARDS
       ====================================================== */

    .insight-card {
        background: rgba(5, 35, 20, 0.78);
        border: 1px solid rgba(32, 255, 138, 0.28);
        border-radius: 12px;
        padding: 15px 17px;
        margin-bottom: 10px;

        box-shadow:
            0 0 15px rgba(32, 255, 138, 0.06),
            inset 0 0 15px rgba(32, 255, 138, 0.015);
    }

    .insight-title {
        color: #20ff8a;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .insight-text {
        color: #d5d5d5;
        font-size: 13px;
        line-height: 1.5;
    }

    /* ======================================================
       RECOMMENDATION CARDS
       ====================================================== */

    .recommendation-card {
        background: rgba(25, 25, 25, 0.92);
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 10px;
    }

    .recommendation-title {
        color: white;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .recommendation-text {
        color: #a8a8a8;
        font-size: 13px;
        line-height: 1.5;
    }

    </style>
    """, unsafe_allow_html=True)


    # ========================================================
    # DATA PREPARATION FOR ANALYSIS
    # ========================================================

    data = filtered_df.copy()

    # --------------------------------------------------------
    # Numeric conversion
    # --------------------------------------------------------

    numeric_columns = [
        "is_canceled",
        "lead_time",
        "adr",
        "stays_in_weekend_nights",
        "stays_in_weekdays_nights",
        "is_repeated_guest"
    ]

    for column in numeric_columns:

        if column in data.columns:

            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            )

    # --------------------------------------------------------
    # Total stay duration
    # --------------------------------------------------------

    data["total_stay_nights"] = (
        data["stays_in_weekend_nights"].fillna(0)
        +
        data["stays_in_weekdays_nights"].fillna(0)
    )

    # --------------------------------------------------------
    # Estimated revenue
    # --------------------------------------------------------

    data["estimated_revenue"] = (
        data["adr"].fillna(0)
        *
        data["total_stay_nights"]
    )

    # ========================================================
    # KPI CALCULATIONS
    # ========================================================

    total_bookings = len(data)

    cancelled_bookings = int(
        data["is_canceled"].fillna(0).sum()
    )

    confirmed_bookings = (
        total_bookings - cancelled_bookings
    )

    cancellation_rate = (
        cancelled_bookings / total_bookings * 100
        if total_bookings > 0
        else 0
    )

    average_adr = data["adr"].mean()

    average_lead_time = data["lead_time"].mean()

    average_stay = data["total_stay_nights"].mean()

    repeat_guest_rate = (
        data["is_repeated_guest"].fillna(0).mean() * 100
    )

    total_estimated_revenue = (
        data["estimated_revenue"].sum()
    )

    estimated_revenue_lost = (
        data.loc[
            data["is_canceled"] == 1,
            "estimated_revenue"
        ].sum()
    )

    # ========================================================
    # PAGE HEADER
    # ========================================================

    st.markdown("""
    <div class="executive-header">

        <div class="executive-title">
            📊 Executive Overview
        </div>

        <div class="executive-subtitle">
            High-level view of hotel booking performance,
            customer behaviour, cancellations and revenue.
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # KPI ROW 1
    # ========================================================

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    with kpi1:

        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">
                🏨 Total Bookings
            </div>
            <div class="kpi-value">
                {total_bookings:,.0f}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with kpi2:

        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">
                ✅ Confirmed Bookings
            </div>
            <div class="kpi-value">
                {confirmed_bookings:,.0f}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with kpi3:

        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">
                ❌ Cancelled Bookings
            </div>
            <div class="kpi-value">
                {cancelled_bookings:,.0f}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with kpi4:

        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">
                📉 Cancellation Rate
            </div>
            <div class="kpi-value">
                {cancellation_rate:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    with kpi5:

        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">
                💰 Average ADR
            </div>
            <div class="kpi-value">
                {average_adr:,.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # KPI ROW 2
    # ========================================================

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    with kpi1:

        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">
                ⏳ Average Lead Time
            </div>
            <div class="kpi-value">
                {average_lead_time:.1f} days
            </div>
        </div>
        """, unsafe_allow_html=True)

    with kpi2:

        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">
                🛏️ Average Stay
            </div>
            <div class="kpi-value">
                {average_stay:.1f} nights
            </div>
        </div>
        """, unsafe_allow_html=True)

    with kpi3:

        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">
                🔁 Repeat Guest Rate
            </div>
            <div class="kpi-value">
                {repeat_guest_rate:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    with kpi4:

        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">
                💵 Estimated Revenue
            </div>
            <div class="kpi-value">
                {total_estimated_revenue:,.0f}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with kpi5:

        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">
                🔻 Revenue Lost
            </div>
            <div class="kpi-value">
                {estimated_revenue_lost:,.0f}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # CHART 1 — BOOKINGS BY HOTEL TYPE
    # ========================================================

    st.markdown(
        '<div class="section-header">🏨 Bookings by Hotel Type</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Distribution of bookings between City and Resort hotels.'
        '</div>',
        unsafe_allow_html=True
    )

    hotel_counts = (
        data["hotel"]
        .value_counts()
        .reset_index()
    )

    hotel_counts.columns = [
        "hotel",
        "bookings"
    ]

    fig_hotel = px.pie(
        hotel_counts,
        names="hotel",
        values="bookings",
        hole=0.55
    )

    fig_hotel.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )

    fig_hotel.update_layout(
        height=390,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        showlegend=True,
        legend=dict(
            orientation="h",
            y=-0.05
        )
    )

    st.plotly_chart(
        fig_hotel,
        use_container_width=True
    )

    # ========================================================
    # CHART 2 — MONTHLY BOOKING TREND
    # ========================================================

    st.markdown(
        '<div class="section-header">📅 Booking Trend by Month</div>',
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

    monthly_bookings = (
        data.groupby(
            "arrival_date_month",
            observed=False
        )
        .size()
        .reset_index(name="bookings")
    )

    monthly_bookings["month_order"] = (
        monthly_bookings["arrival_date_month"]
        .map({
            month: index
            for index, month in enumerate(month_order)
        })
    )

    monthly_bookings = (
        monthly_bookings
        .sort_values("month_order")
    )

    fig_booking_trend = px.line(
        monthly_bookings,
        x="arrival_date_month",
        y="bookings",
        markers=True
    )

    fig_booking_trend.update_layout(
        height=390,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Month",
        yaxis_title="Bookings",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_booking_trend,
        use_container_width=True
    )

    # ========================================================
    # CHART 3 — CANCELLATION TREND
    # ========================================================

    st.markdown(
        '<div class="section-header">❌ Monthly Cancellation Trend</div>',
        unsafe_allow_html=True
    )

    monthly_cancellation = (
        data.groupby(
            "arrival_date_month",
            observed=False
        )
        .agg(
            total_bookings=("is_canceled", "size"),
            cancelled_bookings=("is_canceled", "sum")
        )
        .reset_index()
    )

    monthly_cancellation["cancellation_rate"] = (
        monthly_cancellation["cancelled_bookings"]
        /
        monthly_cancellation["total_bookings"]
        *
        100
    )

    monthly_cancellation["month_order"] = (
        monthly_cancellation["arrival_date_month"]
        .map({
            month: index
            for index, month in enumerate(month_order)
        })
    )

    monthly_cancellation = (
        monthly_cancellation
        .sort_values("month_order")
    )

    fig_cancellation = px.line(
        monthly_cancellation,
        x="arrival_date_month",
        y="cancellation_rate",
        markers=True
    )

    fig_cancellation.update_layout(
        height=390,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Month",
        yaxis_title="Cancellation Rate (%)",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_cancellation,
        use_container_width=True
    )

    # ========================================================
    # CHART 4 — ADR BY MONTH
    # ========================================================

    st.markdown(
        '<div class="section-header">💰 Average ADR by Month</div>',
        unsafe_allow_html=True
    )

    monthly_adr = (
        data.groupby(
            "arrival_date_month",
            observed=False
        )["adr"]
        .mean()
        .reset_index()
    )

    monthly_adr["month_order"] = (
        monthly_adr["arrival_date_month"]
        .map({
            month: index
            for index, month in enumerate(month_order)
        })
    )

    monthly_adr = (
        monthly_adr
        .sort_values("month_order")
    )

    fig_adr = px.line(
        monthly_adr,
        x="arrival_date_month",
        y="adr",
        markers=True
    )

    fig_adr.update_layout(
        height=390,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Month",
        yaxis_title="Average ADR",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_adr,
        use_container_width=True
    )

    # ========================================================
    # CHART 5 — MARKET SEGMENT
    # ========================================================

    st.markdown(
        '<div class="section-header">📢 Bookings by Market Segment</div>',
        unsafe_allow_html=True
    )

    market_counts = (
        data["market_segment"]
        .value_counts()
        .reset_index()
    )

    market_counts.columns = [
        "market_segment",
        "bookings"
    ]

    market_counts = (
        market_counts
        .sort_values("bookings", ascending=True)
    )

    fig_market = px.bar(
        market_counts,
        x="bookings",
        y="market_segment",
        orientation="h"
    )

    fig_market.update_layout(
        height=430,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Bookings",
        yaxis_title="Market Segment"
    )

    st.plotly_chart(
        fig_market,
        use_container_width=True
    )

    # ========================================================
    # CHART 6 — CUSTOMER TYPE
    # ========================================================

    st.markdown(
        '<div class="section-header">👥 Bookings by Customer Type</div>',
        unsafe_allow_html=True
    )

    customer_counts = (
        data["customer_type"]
        .value_counts()
        .reset_index()
    )

    customer_counts.columns = [
        "customer_type",
        "bookings"
    ]

    customer_counts = (
        customer_counts
        .sort_values("bookings", ascending=True)
    )

    fig_customer = px.bar(
        customer_counts,
        x="bookings",
        y="customer_type",
        orientation="h"
    )

    fig_customer.update_layout(
        height=430,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Bookings",
        yaxis_title="Customer Type"
    )

    st.plotly_chart(
        fig_customer,
        use_container_width=True
    )

    # ========================================================
    # EXECUTIVE INSIGHTS
    # ========================================================

    st.markdown(
        '<div class="section-header">📌 Executive Insights</div>',
        unsafe_allow_html=True
    )

    insights = []

    # --------------------------------------------------------
    # Hotel insight
    # --------------------------------------------------------

    hotel_share = (
        data["hotel"]
        .value_counts(normalize=True)
        * 100
    )

    if not hotel_share.empty:

        top_hotel = hotel_share.idxmax()
        top_hotel_percentage = hotel_share.max()

        insights.append(
            f"{top_hotel} accounts for "
            f"{top_hotel_percentage:.1f}% of the bookings "
            f"in the current selection."
        )

    # --------------------------------------------------------
    # Cancellation insight
    # --------------------------------------------------------

    if not monthly_cancellation.empty:

        highest_cancel_month = (
            monthly_cancellation
            .loc[
                monthly_cancellation[
                    "cancellation_rate"
                ].idxmax(),
                "arrival_date_month"
            ]
        )

        highest_cancel_rate = (
            monthly_cancellation[
                "cancellation_rate"
            ].max()
        )

        insights.append(
            f"{highest_cancel_month} has the highest "
            f"monthly cancellation rate at "
            f"{highest_cancel_rate:.1f}%."
        )

    # --------------------------------------------------------
    # Market segment insight
    # --------------------------------------------------------

    if not market_counts.empty:

        dominant_market = (
            market_counts
            .sort_values(
                "bookings",
                ascending=False
            )
            .iloc[0]
        )

        insights.append(
            f"{dominant_market['market_segment']} is the "
            f"dominant market segment with "
            f"{dominant_market['bookings']:,.0f} bookings."
        )

    # --------------------------------------------------------
    # ADR insight
    # --------------------------------------------------------

    if not monthly_adr.empty:

        highest_adr_month = (
            monthly_adr
            .loc[
                monthly_adr["adr"].idxmax(),
                "arrival_date_month"
            ]
        )

        highest_adr_value = (
            monthly_adr["adr"].max()
        )

        insights.append(
            f"{highest_adr_month} records the highest "
            f"average ADR at {highest_adr_value:,.2f}."
        )

    # --------------------------------------------------------
    # Repeat guest insight
    # --------------------------------------------------------

    if repeat_guest_rate > 0:

        insights.append(
            f"Repeat guests represent "
            f"{repeat_guest_rate:.1f}% of bookings, "
            f"indicating the current level of guest retention."
        )

    # --------------------------------------------------------
    # Display maximum 5 insights
    # --------------------------------------------------------

    for index, insight in enumerate(
        insights[:5],
        start=1
    ):

        st.markdown(f"""
        <div class="insight-card">

            <div class="insight-title">
                📌 Insight {index}
            </div>

            <div class="insight-text">
                {insight}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    st.markdown(
        '<div class="section-header">💡 Recommendations</div>',
        unsafe_allow_html=True
    )

    recommendations = []

    # --------------------------------------------------------
    # Cancellation recommendation
    # --------------------------------------------------------

    if cancellation_rate >= 30:

        recommendations.append((
            "Reduce Cancellation Exposure",
            "The cancellation rate is relatively high. "
            "Consider stronger deposit policies, "
            "clearer cancellation deadlines and automated "
            "pre-arrival reminders for higher-risk bookings."
        ))

    else:

        recommendations.append((
            "Maintain Cancellation Controls",
            "The current cancellation level is comparatively "
            "controlled. Continue monitoring cancellation "
            "patterns by month, hotel and booking segment."
        ))

    # --------------------------------------------------------
    # Seasonal recommendation
    # --------------------------------------------------------

    if not monthly_bookings.empty:

        peak_month = (
            monthly_bookings
            .loc[
                monthly_bookings["bookings"].idxmax(),
                "arrival_date_month"
            ]
        )

        recommendations.append((
            "Optimize Seasonal Pricing",
            f"{peak_month} has the highest booking volume "
            "in the current selection. Consider dynamic "
            "pricing and inventory optimization during "
            "high-demand periods."
        ))

    # --------------------------------------------------------
    # Market recommendation
    # --------------------------------------------------------

    if not market_counts.empty:

        top_market = (
            market_counts
            .sort_values(
                "bookings",
                ascending=False
            )
            .iloc[0]["market_segment"]
        )

        recommendations.append((
            "Focus on High-Volume Channels",
            f"{top_market} is currently the largest market "
            "segment. Monitor its profitability and "
            "cancellation behaviour while maintaining "
            "diversification across other channels."
        ))

    # --------------------------------------------------------
    # Repeat guest recommendation
    # --------------------------------------------------------

    if repeat_guest_rate < 20:

        recommendations.append((
            "Strengthen Guest Retention",
            "The repeat guest share is relatively low. "
            "Consider loyalty benefits, personalized offers "
            "and post-stay engagement campaigns to encourage "
            "repeat bookings."
        ))

    else:

        recommendations.append((
            "Strengthen Guest Loyalty",
            "Repeat guests form a meaningful portion of the "
            "current bookings. Consider loyalty programs and "
            "personalized offers to further increase retention."
        ))

    # --------------------------------------------------------
    # Display recommendations
    # --------------------------------------------------------

    for index, recommendation in enumerate(
        recommendations[:4],
        start=1
    ):

        title, description = recommendation

        st.markdown(f"""
        <div class="recommendation-card">

            <div class="recommendation-title">
                💡 Recommendation {index} — {title}
            </div>

            <div class="recommendation-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

# ============================================================
# HOTEL PERFORMANCE ANALYSIS
# ============================================================

def render_hotel_performance_analysis(df):

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    if df is None or df.empty:
        st.warning("⚠️ No data available for hotel performance analysis.")
        return

    data = df.copy()

    # --------------------------------------------------------
    # NUMERIC CONVERSION
    # --------------------------------------------------------

    numeric_columns = [
        "is_canceled",
        "lead_time",
        "adr",
        "stays_in_weekend_nights",
        "stays_in_weekdays_nights"
    ]

    for column in numeric_columns:

        if column in data.columns:

            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            )

    # --------------------------------------------------------
    # CALCULATED COLUMNS
    # --------------------------------------------------------

    data["total_stay_nights"] = (
        data["stays_in_weekend_nights"].fillna(0)
        +
        data["stays_in_weekdays_nights"].fillna(0)
    )

    data["estimated_revenue"] = (
        data["adr"].fillna(0)
        *
        data["total_stay_nights"]
    )

    # ========================================================
    # PAGE CSS
    # ========================================================

    st.markdown("""
    <style>

    /* ======================================================
       PAGE HEADER
       ====================================================== */

    .hotel-performance-header {
        margin-top: 10px;
        margin-bottom: 25px;
    }

    .hotel-performance-title {
        font-size: 32px;
        font-weight: 700;
        color: white;
        margin-bottom: 5px;
    }

    .hotel-performance-subtitle {
        font-size: 14px;
        color: #9b9b9b;
    }

    /* ======================================================
       HOTEL KPI CARDS
       ====================================================== */

    .hotel-performance-kpi {
        background: rgba(20, 20, 20, 0.90);

        border: 1px solid rgba(255,255,255,0.10);

        border-radius: 14px;

        padding: 17px;

        min-height: 105px;

        margin-bottom: 14px;

        box-shadow:
            0 7px 25px rgba(0,0,0,0.30),
            inset 0 0 18px rgba(255,255,255,0.015);

        transition: all 0.25s ease;
    }

    .hotel-performance-kpi:hover {

        transform: translateY(-3px);

        border-color: rgba(32,255,138,0.35);

        box-shadow:
            0 8px 28px rgba(0,0,0,0.35),
            0 0 20px rgba(32,255,138,0.10);
    }

    .hotel-performance-kpi-label {

        color: #999999;

        font-size: 11px;

        font-weight: 600;

        margin-bottom: 8px;
    }

    .hotel-performance-kpi-value {

        color: white;

        font-size: 23px;

        font-weight: 700;
    }

    /* ======================================================
       HOTEL LABEL
       ====================================================== */

    .hotel-name {

        color: #20ff8a;

        font-size: 18px;

        font-weight: 700;

        margin-top: 10px;

        margin-bottom: 12px;
    }

    /* ======================================================
       SECTION TITLE
       ====================================================== */

    .hotel-performance-section {

        color: white;

        font-size: 19px;

        font-weight: 700;

        margin-top: 28px;

        margin-bottom: 5px;
    }

    .hotel-performance-description {

        color: #8d8d8d;

        font-size: 13px;

        margin-bottom: 15px;
    }

    /* ======================================================
       INSIGHT CARDS
       ====================================================== */

    .hotel-performance-insight {

        background: rgba(4,35,20,0.82);

        border: 1px solid rgba(32,255,138,0.25);

        border-radius: 12px;

        padding: 15px 17px;

        margin-bottom: 10px;

        box-shadow:
            0 0 18px rgba(32,255,138,0.06);
    }

    .hotel-performance-insight-title {

        color: #20ff8a;

        font-size: 14px;

        font-weight: 700;

        margin-bottom: 5px;
    }

    .hotel-performance-insight-text {

        color: #d4d4d4;

        font-size: 13px;

        line-height: 1.5;
    }

    /* ======================================================
       RECOMMENDATION CARDS
       ====================================================== */

    .hotel-performance-recommendation {

        background: rgba(20,20,20,0.92);

        border: 1px solid rgba(255,255,255,0.10);

        border-radius: 12px;

        padding: 16px 18px;

        margin-bottom: 10px;
    }

    .hotel-performance-recommendation-title {

        color: white;

        font-size: 14px;

        font-weight: 700;

        margin-bottom: 5px;
    }

    .hotel-performance-recommendation-text {

        color: #a5a5a5;

        font-size: 13px;

        line-height: 1.5;
    }

    </style>
    """, unsafe_allow_html=True)

    # ========================================================
    # HEADER
    # ========================================================

    st.markdown("""
    <div class="hotel-performance-header">

        <div class="hotel-performance-title">
            🏨 Hotel Performance Analysis
        </div>

        <div class="hotel-performance-subtitle">
            Compare City Hotel and Resort Hotel performance
            across bookings, pricing, cancellations,
            lead time, stay duration and revenue.
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # HOTEL DATA
    # ========================================================

    hotel_summary = (
        data
        .groupby("hotel")
        .agg(
            total_bookings=("hotel", "size"),
            cancellation_rate=("is_canceled", "mean"),
            average_adr=("adr", "mean"),
            average_lead_time=("lead_time", "mean"),
            average_stay=("total_stay_nights", "mean"),
            average_revenue=("estimated_revenue", "mean"),
            total_revenue=("estimated_revenue", "sum")
        )
        .reset_index()
    )

    # Convert cancellation rate to percentage

    hotel_summary["cancellation_rate"] = (
        hotel_summary["cancellation_rate"] * 100
    )

    # Booking share

    hotel_summary["booking_share"] = (
        hotel_summary["total_bookings"]
        /
        hotel_summary["total_bookings"].sum()
        *
        100
    )

    # ========================================================
    # HOTEL KPI SECTIONS
    # ========================================================

    st.markdown(
        '<div class="hotel-performance-section">'
        '📊 Hotel Performance KPIs'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="hotel-performance-description">'
        'Key performance indicators for each hotel type.'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # CITY HOTEL
    # --------------------------------------------------------

    city_data = hotel_summary[
        hotel_summary["hotel"] == "City Hotel"
    ]

    if not city_data.empty:

        city = city_data.iloc[0]

        st.markdown(
            '<div class="hotel-name">'
            '🏙️ City Hotel'
            '</div>',
            unsafe_allow_html=True
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown(f"""
            <div class="hotel-performance-kpi">
                <div class="hotel-performance-kpi-label">
                    TOTAL BOOKINGS
                </div>
                <div class="hotel-performance-kpi-value">
                    {city['total_bookings']:,.0f}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class="hotel-performance-kpi">
                <div class="hotel-performance-kpi-label">
                    BOOKING SHARE
                </div>
                <div class="hotel-performance-kpi-value">
                    {city['booking_share']:.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div class="hotel-performance-kpi">
                <div class="hotel-performance-kpi-label">
                    CANCELLATION RATE
                </div>
                <div class="hotel-performance-kpi-value">
                    {city['cancellation_rate']:.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c4:
            st.markdown(f"""
            <div class="hotel-performance-kpi">
                <div class="hotel-performance-kpi-label">
                    AVERAGE ADR
                </div>
                <div class="hotel-performance-kpi-value">
                    {city['average_adr']:,.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown(f"""
            <div class="hotel-performance-kpi">
                <div class="hotel-performance-kpi-label">
                    AVERAGE LEAD TIME
                </div>
                <div class="hotel-performance-kpi-value">
                    {city['average_lead_time']:.1f} days
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class="hotel-performance-kpi">
                <div class="hotel-performance-kpi-label">
                    AVERAGE STAY
                </div>
                <div class="hotel-performance-kpi-value">
                    {city['average_stay']:.1f} nights
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div class="hotel-performance-kpi">
                <div class="hotel-performance-kpi-label">
                    AVERAGE REVENUE
                </div>
                <div class="hotel-performance-kpi-value">
                    {city['average_revenue']:,.0f}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # RESORT HOTEL
    # --------------------------------------------------------

    resort_data = hotel_summary[
        hotel_summary["hotel"] == "Resort Hotel"
    ]

    if not resort_data.empty:

        resort = resort_data.iloc[0]

        st.markdown(
            '<div class="hotel-name">'
            '🌴 Resort Hotel'
            '</div>',
            unsafe_allow_html=True
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown(f"""
            <div class="hotel-performance-kpi">
                <div class="hotel-performance-kpi-label">
                    TOTAL BOOKINGS
                </div>
                <div class="hotel-performance-kpi-value">
                    {resort['total_bookings']:,.0f}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class="hotel-performance-kpi">
                <div class="hotel-performance-kpi-label">
                    BOOKING SHARE
                </div>
                <div class="hotel-performance-kpi-value">
                    {resort['booking_share']:.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div class="hotel-performance-kpi">
                <div class="hotel-performance-kpi-label">
                    CANCELLATION RATE
                </div>
                <div class="hotel-performance-kpi-value">
                    {resort['cancellation_rate']:.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c4:
            st.markdown(f"""
            <div class="hotel-performance-kpi">
                <div class="hotel-performance-kpi-label">
                    AVERAGE ADR
                </div>
                <div class="hotel-performance-kpi-value">
                    {resort['average_adr']:,.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown(f"""
            <div class="hotel-performance-kpi">
                <div class="hotel-performance-kpi-label">
                    AVERAGE LEAD TIME
                </div>
                <div class="hotel-performance-kpi-value">
                    {resort['average_lead_time']:.1f} days
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class="hotel-performance-kpi">
                <div class="hotel-performance-kpi-label">
                    AVERAGE STAY
                </div>
                <div class="hotel-performance-kpi-value">
                    {resort['average_stay']:.1f} nights
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div class="hotel-performance-kpi">
                <div class="hotel-performance-kpi-label">
                    AVERAGE REVENUE
                </div>
                <div class="hotel-performance-kpi-value">
                    {resort['average_revenue']:,.0f}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ========================================================
    # CHART 1 — HOTEL DISTRIBUTION
    # ========================================================

    st.markdown(
        '<div class="hotel-performance-section">'
        '🏨 Hotel Distribution'
        '</div>',
        unsafe_allow_html=True
    )

    fig_distribution = px.bar(
        hotel_summary.sort_values(
            "total_bookings",
            ascending=True
        ),
        x="total_bookings",
        y="hotel",
        orientation="h",
        text="total_bookings"
    )

    fig_distribution.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig_distribution.update_layout(
        height=350,
        margin=dict(
            l=20,
            r=40,
            t=20,
            b=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Bookings",
        yaxis_title=""
    )

    st.plotly_chart(
        fig_distribution,
        use_container_width=True
    )

    # ========================================================
    # CHART 2 + 3
    # ========================================================

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # ADR COMPARISON
    # --------------------------------------------------------

    with col1:

        st.markdown(
            '<div class="hotel-performance-section">'
            '💰 ADR Comparison'
            '</div>',
            unsafe_allow_html=True
        )

        fig_adr = px.bar(
            hotel_summary,
            x="hotel",
            y="average_adr",
            text="average_adr"
        )

        fig_adr.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside"
        )

        fig_adr.update_layout(
            height=380,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis_title="",
            yaxis_title="Average ADR"
        )

        st.plotly_chart(
            fig_adr,
            use_container_width=True
        )

    # --------------------------------------------------------
    # CANCELLATION RATE
    # --------------------------------------------------------

    with col2:

        st.markdown(
            '<div class="hotel-performance-section">'
            '❌ Cancellation Rate'
            '</div>',
            unsafe_allow_html=True
        )

        fig_cancel = px.bar(
            hotel_summary,
            x="hotel",
            y="cancellation_rate",
            text="cancellation_rate"
        )

        fig_cancel.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )

        fig_cancel.update_layout(
            height=380,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis_title="",
            yaxis_title="Cancellation Rate (%)"
        )

        st.plotly_chart(
            fig_cancel,
            use_container_width=True
        )

    # ========================================================
    # CHART 4 + 5
    # ========================================================

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # LEAD TIME
    # --------------------------------------------------------

    with col1:

        st.markdown(
            '<div class="hotel-performance-section">'
            '⏳ Average Lead Time'
            '</div>',
            unsafe_allow_html=True
        )

        fig_lead = px.bar(
            hotel_summary,
            x="hotel",
            y="average_lead_time",
            text="average_lead_time"
        )

        fig_lead.update_traces(
            texttemplate="%{text:.1f} days",
            textposition="outside"
        )

        fig_lead.update_layout(
            height=380,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis_title="",
            yaxis_title="Average Lead Time (Days)"
        )

        st.plotly_chart(
            fig_lead,
            use_container_width=True
        )

    # --------------------------------------------------------
    # AVERAGE STAY
    # --------------------------------------------------------

    with col2:

        st.markdown(
            '<div class="hotel-performance-section">'
            '🛏️ Average Stay'
            '</div>',
            unsafe_allow_html=True
        )

        fig_stay = px.bar(
            hotel_summary,
            x="hotel",
            y="average_stay",
            text="average_stay"
        )

        fig_stay.update_traces(
            texttemplate="%{text:.1f} nights",
            textposition="outside"
        )

        fig_stay.update_layout(
            height=380,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis_title="",
            yaxis_title="Average Stay (Nights)"
        )

        st.plotly_chart(
            fig_stay,
            use_container_width=True
        )

    # ========================================================
    # CHART 6 — MONTHLY HOTEL PERFORMANCE
    # ========================================================

    st.markdown(
        '<div class="hotel-performance-section">'
        '📅 Monthly Hotel Performance'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="hotel-performance-description">'
        'Monthly booking volume comparison between City Hotel '
        'and Resort Hotel.'
        '</div>',
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

    month_map = {
        month: index
        for index, month in enumerate(month_order)
    }

    monthly_hotel = (
        data
        .groupby(
            [
                "arrival_date_month",
                "hotel"
            ],
            observed=False
        )
        .size()
        .reset_index(
            name="bookings"
        )
    )

    monthly_hotel["month_order"] = (
        monthly_hotel[
            "arrival_date_month"
        ].map(month_map)
    )

    monthly_hotel = (
        monthly_hotel
        .sort_values("month_order")
    )

    fig_monthly_hotel = px.line(
        monthly_hotel,
        x="arrival_date_month",
        y="bookings",
        color="hotel",
        markers=True
    )

    fig_monthly_hotel.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Month",
        yaxis_title="Bookings",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_monthly_hotel,
        use_container_width=True
    )

    # ========================================================
    # REVENUE COMPARISON
    # ========================================================

    st.markdown(
        '<div class="hotel-performance-section">'
        '💵 Estimated Revenue Comparison'
        '</div>',
        unsafe_allow_html=True
    )

    fig_revenue = px.bar(
        hotel_summary,
        x="hotel",
        y="total_revenue",
        text="total_revenue"
    )

    fig_revenue.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside"
    )

    fig_revenue.update_layout(
        height=380,
        margin=dict(
            l=20,
            r=40,
            t=20,
            b=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="",
        yaxis_title="Estimated Revenue"
    )

    st.plotly_chart(
        fig_revenue,
        use_container_width=True
    )

    # ========================================================
    # HOTEL PERFORMANCE INSIGHTS
    # ========================================================

    st.markdown(
        '<div class="hotel-performance-section">'
        '📌 Hotel Performance Insights'
        '</div>',
        unsafe_allow_html=True
    )

    insights = []

    # --------------------------------------------------------
    # Bookings
    # --------------------------------------------------------

    top_booking_hotel = (
        hotel_summary
        .loc[
            hotel_summary["total_bookings"].idxmax()
        ]
    )

    insights.append(
        f"{top_booking_hotel['hotel']} receives the highest "
        f"number of bookings with "
        f"{top_booking_hotel['total_bookings']:,.0f} bookings, "
        f"representing {top_booking_hotel['booking_share']:.1f}% "
        f"of total bookings."
    )

    # --------------------------------------------------------
    # ADR
    # --------------------------------------------------------

    highest_adr_hotel = (
        hotel_summary
        .loc[
            hotel_summary["average_adr"].idxmax()
        ]
    )

    insights.append(
        f"{highest_adr_hotel['hotel']} has the higher average "
        f"ADR at {highest_adr_hotel['average_adr']:,.2f}, "
        f"indicating stronger average room pricing."
    )

    # --------------------------------------------------------
    # Cancellation
    # --------------------------------------------------------

    highest_cancel_hotel = (
        hotel_summary
        .loc[
            hotel_summary["cancellation_rate"].idxmax()
        ]
    )

    insights.append(
        f"{highest_cancel_hotel['hotel']} has the higher "
        f"cancellation risk, with a cancellation rate of "
        f"{highest_cancel_hotel['cancellation_rate']:.1f}%."
    )

    # --------------------------------------------------------
    # Stay duration
    # --------------------------------------------------------

    longest_stay_hotel = (
        hotel_summary
        .loc[
            hotel_summary["average_stay"].idxmax()
        ]
    )

    insights.append(
        f"{longest_stay_hotel['hotel']} has the longer average "
        f"stay at {longest_stay_hotel['average_stay']:.1f} nights."
    )

    # --------------------------------------------------------
    # Revenue
    # --------------------------------------------------------

    highest_revenue_hotel = (
        hotel_summary
        .loc[
            hotel_summary["total_revenue"].idxmax()
        ]
    )

    insights.append(
        f"{highest_revenue_hotel['hotel']} generates the higher "
        f"estimated total revenue at "
        f"{highest_revenue_hotel['total_revenue']:,.0f}."
    )

    # --------------------------------------------------------
    # DISPLAY INSIGHTS
    # --------------------------------------------------------

    for i, insight in enumerate(
        insights,
        start=1
    ):

        st.markdown(f"""
        <div class="hotel-performance-insight">

            <div class="hotel-performance-insight-title">
                📌 Insight {i}
            </div>

            <div class="hotel-performance-insight-text">
                {insight}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # HOTEL-SPECIFIC RECOMMENDATIONS
    # ========================================================

    st.markdown(
        '<div class="hotel-performance-section">'
        '💡 Hotel-Specific Recommendations'
        '</div>',
        unsafe_allow_html=True
    )

    recommendations = []

    # --------------------------------------------------------
    # City Hotel recommendation
    # --------------------------------------------------------

    if not city_data.empty:

        city = city_data.iloc[0]

        if city["cancellation_rate"] > resort["cancellation_rate"]:

            recommendations.append((
                "🏙️ City Hotel — Reduce Cancellation Risk",
                f"City Hotel has a higher cancellation rate "
                f"of {city['cancellation_rate']:.1f}%. "
                "Consider stronger booking confirmation "
                "strategies, deposits for high-risk bookings "
                "and automated pre-arrival reminders."
            ))

        else:

            recommendations.append((
                "🏙️ City Hotel — Protect Booking Stability",
                "City Hotel currently has a comparatively "
                "controlled cancellation rate. Continue "
                "monitoring cancellation patterns by month "
                "and booking channel."
            ))

        recommendations.append((
            "🏙️ City Hotel — Optimize Demand",
            "Use demand-based pricing and inventory controls "
            "during high-volume periods to maximize revenue "
            "while maintaining healthy occupancy."
        ))

    # --------------------------------------------------------
    # Resort Hotel recommendation
    # --------------------------------------------------------

    if not resort_data.empty:

        resort = resort_data.iloc[0]

        if resort["average_stay"] > city["average_stay"]:

            recommendations.append((
                "🌴 Resort Hotel — Encourage Longer Stays",
                f"Resort Hotel has the longer average stay "
                f"at {resort['average_stay']:.1f} nights. "
                "Promote multi-night packages and extended-stay "
                "offers to further increase guest value."
            ))

        else:

            recommendations.append((
                "🌴 Resort Hotel — Increase Stay Duration",
                "Consider bundled packages, activities and "
                "extended-stay discounts to encourage guests "
                "to remain longer."
            ))

        if resort["average_adr"] > city["average_adr"]:

            recommendations.append((
                "🌴 Resort Hotel — Leverage Premium Pricing",
                f"Resort Hotel achieves a higher average ADR "
                f"of {resort['average_adr']:,.2f}. "
                "Continue positioning premium experiences "
                "and packages to support higher room rates."
            ))

        else:

            recommendations.append((
                "🌴 Resort Hotel — Improve Revenue per Stay",
                "Explore premium room packages, experiences "
                "and value-added services to improve revenue "
                "per booking."
            ))

    # --------------------------------------------------------
    # DISPLAY RECOMMENDATIONS
    # --------------------------------------------------------

    for i, recommendation in enumerate(
        recommendations[:4],
        start=1
    ):

        title, description = recommendation

        st.markdown(f"""
        <div class="hotel-performance-recommendation">

            <div class="hotel-performance-recommendation-title">
                💡 Recommendation {i} — {title}
            </div>

            <div class="hotel-performance-recommendation-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

# ============================================================
# BOOKING TREND ANALYSIS
# ============================================================

def render_booking_trend_analysis(df):

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    if df is None or df.empty:
        st.warning("⚠️ No data available for booking trend analysis.")
        return

    data = df.copy()

    # --------------------------------------------------------
    # NUMERIC CONVERSION
    # --------------------------------------------------------

    numeric_columns = [
        "is_canceled",
        "lead_time",
        "adr",
        "arrival_date_day_of_month",
        "arrival_date_week_number",
        "stays_in_weekend_nights",
        "stays_in_weekdays_nights"
    ]

    for column in numeric_columns:

        if column in data.columns:

            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            )

    # --------------------------------------------------------
    # CALCULATED COLUMNS
    # --------------------------------------------------------

    data["total_stay_nights"] = (
        data["stays_in_weekend_nights"].fillna(0)
        +
        data["stays_in_weekdays_nights"].fillna(0)
    )

    data["estimated_revenue"] = (
        data["adr"].fillna(0)
        *
        data["total_stay_nights"]
    )

    # ========================================================
    # PAGE CSS
    # ========================================================

    st.markdown("""
    <style>

    /* ======================================================
       PAGE HEADER
       ====================================================== */

    .booking-trend-header {
        margin-top: 10px;
        margin-bottom: 25px;
    }

    .booking-trend-title {
        font-size: 32px;
        font-weight: 700;
        color: white;
        margin-bottom: 5px;
    }

    .booking-trend-subtitle {
        font-size: 14px;
        color: #9b9b9b;
    }

    /* ======================================================
       KPI CARDS
       ====================================================== */

    .booking-trend-kpi {

        background: rgba(20,20,20,0.90);

        border: 1px solid rgba(255,255,255,0.10);

        border-radius: 14px;

        padding: 18px;

        min-height: 110px;

        margin-bottom: 15px;

        box-shadow:
            0 7px 25px rgba(0,0,0,0.30),
            inset 0 0 18px rgba(255,255,255,0.015);

        transition: all 0.25s ease;
    }

    .booking-trend-kpi:hover {

        transform: translateY(-3px);

        border-color: rgba(32,255,138,0.35);

        box-shadow:
            0 8px 28px rgba(0,0,0,0.35),
            0 0 20px rgba(32,255,138,0.10);
    }

    .booking-trend-kpi-label {

        color: #999999;

        font-size: 11px;

        font-weight: 600;

        margin-bottom: 8px;
    }

    .booking-trend-kpi-value {

        color: white;

        font-size: 22px;

        font-weight: 700;
    }

    /* ======================================================
       SECTION TITLE
       ====================================================== */

    .booking-trend-section {

        color: white;

        font-size: 19px;

        font-weight: 700;

        margin-top: 28px;

        margin-bottom: 5px;
    }

    .booking-trend-description {

        color: #8d8d8d;

        font-size: 13px;

        margin-bottom: 15px;
    }

    /* ======================================================
       INSIGHT CARDS
       ====================================================== */

    .booking-trend-insight {

        background: rgba(4,35,20,0.82);

        border: 1px solid rgba(32,255,138,0.25);

        border-radius: 12px;

        padding: 15px 17px;

        margin-bottom: 10px;

        box-shadow:
            0 0 18px rgba(32,255,138,0.06);
    }

    .booking-trend-insight-title {

        color: #20ff8a;

        font-size: 14px;

        font-weight: 700;

        margin-bottom: 5px;
    }

    .booking-trend-insight-text {

        color: #d4d4d4;

        font-size: 13px;

        line-height: 1.5;
    }

    /* ======================================================
       RECOMMENDATION CARDS
       ====================================================== */

    .booking-trend-recommendation {

        background: rgba(20,20,20,0.92);

        border: 1px solid rgba(255,255,255,0.10);

        border-radius: 12px;

        padding: 16px 18px;

        margin-bottom: 10px;
    }

    .booking-trend-recommendation-title {

        color: white;

        font-size: 14px;

        font-weight: 700;

        margin-bottom: 5px;
    }

    .booking-trend-recommendation-text {

        color: #a5a5a5;

        font-size: 13px;

        line-height: 1.5;
    }

    </style>
    """, unsafe_allow_html=True)

    # ========================================================
    # PAGE HEADER
    # ========================================================

    st.markdown("""
    <div class="booking-trend-header">

        <div class="booking-trend-title">
            📅 Booking Trend Analysis
        </div>

        <div class="booking-trend-subtitle">
            Analyze booking demand, seasonality, arrival patterns,
            cancellation behaviour, pricing and revenue trends.
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # MONTH ORDER
    # ========================================================

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

    month_map = {
        month: index
        for index, month in enumerate(month_order)
    }

    # ========================================================
    # MONTHLY DATA
    # ========================================================

    monthly_data = (
        data
        .groupby(
            "arrival_date_month",
            observed=False
        )
        .agg(
            bookings=("hotel", "size"),
            cancellations=("is_canceled", "sum"),
            adr=("adr", "mean"),
            revenue=("estimated_revenue", "sum")
        )
        .reset_index()
    )

    monthly_data["cancellation_rate"] = (
        monthly_data["cancellations"]
        /
        monthly_data["bookings"]
        *
        100
    )

    monthly_data["month_order"] = (
        monthly_data[
            "arrival_date_month"
        ].map(month_map)
    )

    monthly_data = (
        monthly_data
        .sort_values("month_order")
    )

    # ========================================================
    # KPI CALCULATIONS
    # ========================================================

    peak_booking_row = (
        monthly_data
        .loc[
            monthly_data["bookings"].idxmax()
        ]
    )

    lowest_booking_row = (
        monthly_data
        .loc[
            monthly_data["bookings"].idxmin()
        ]
    )

    peak_booking_month = (
        peak_booking_row["arrival_date_month"]
    )

    lowest_booking_month = (
        lowest_booking_row["arrival_date_month"]
    )

    peak_arrival_month = peak_booking_month

    average_monthly_bookings = (
        monthly_data["bookings"].mean()
    )

    # --------------------------------------------------------
    # Peak Season
    #
    # Define peak season as the three months with the
    # highest booking volume.
    # --------------------------------------------------------

    peak_season_months = (
        monthly_data
        .nlargest(
            3,
            "bookings"
        )["arrival_date_month"]
        .tolist()
    )

    peak_season = ", ".join(
        peak_season_months
    )

    # ========================================================
    # KPI CARDS
    # ========================================================

    st.markdown(
        '<div class="booking-trend-section">'
        '📊 Booking Trend KPIs'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="booking-trend-description">'
        'Key indicators showing when booking demand is highest '
        'and lowest.'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    # --------------------------------------------------------
    # Peak Booking Month
    # --------------------------------------------------------

    with col1:

        st.markdown(f"""
        <div class="booking-trend-kpi">

            <div class="booking-trend-kpi-label">
                🔥 PEAK BOOKING MONTH
            </div>

            <div class="booking-trend-kpi-value">
                {peak_booking_month}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # Lowest Booking Month
    # --------------------------------------------------------

    with col2:

        st.markdown(f"""
        <div class="booking-trend-kpi">

            <div class="booking-trend-kpi-label">
                📉 LOWEST BOOKING MONTH
            </div>

            <div class="booking-trend-kpi-value">
                {lowest_booking_month}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # Peak Arrival Month
    # --------------------------------------------------------

    with col3:

        st.markdown(f"""
        <div class="booking-trend-kpi">

            <div class="booking-trend-kpi-label">
                🛬 PEAK ARRIVAL MONTH
            </div>

            <div class="booking-trend-kpi-value">
                {peak_arrival_month}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # Average Monthly Bookings
    # --------------------------------------------------------

    with col4:

        st.markdown(f"""
        <div class="booking-trend-kpi">

            <div class="booking-trend-kpi-label">
                📊 AVG MONTHLY BOOKINGS
            </div>

            <div class="booking-trend-kpi-value">
                {average_monthly_bookings:,.0f}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # Peak Season
    # --------------------------------------------------------

    with col5:

        st.markdown(f"""
        <div class="booking-trend-kpi">

            <div class="booking-trend-kpi-label">
                ☀️ PEAK SEASON
            </div>

            <div class="booking-trend-kpi-value">
                {peak_season}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # CHART 1 — MONTHLY BOOKINGS
    # ========================================================

    st.markdown(
        '<div class="booking-trend-section">'
        '📈 Monthly Bookings'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="booking-trend-description">'
        'Monthly booking volume reveals seasonal demand patterns.'
        '</div>',
        unsafe_allow_html=True
    )

    fig_monthly_bookings = px.line(
        monthly_data,
        x="arrival_date_month",
        y="bookings",
        markers=True
    )

    fig_monthly_bookings.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Month",
        yaxis_title="Bookings",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_monthly_bookings,
        use_container_width=True
    )

    # ========================================================
    # CHART 2 — MONTHLY BOOKINGS BY HOTEL
    # ========================================================

    st.markdown(
        '<div class="booking-trend-section">'
        '🏨 Monthly Bookings by Hotel'
        '</div>',
        unsafe_allow_html=True
    )

    hotel_monthly = (
        data
        .groupby(
            [
                "arrival_date_month",
                "hotel"
            ],
            observed=False
        )
        .size()
        .reset_index(
            name="bookings"
        )
    )

    hotel_monthly["month_order"] = (
        hotel_monthly[
            "arrival_date_month"
        ].map(month_map)
    )

    hotel_monthly = (
        hotel_monthly
        .sort_values("month_order")
    )

    fig_hotel_monthly = px.line(
        hotel_monthly,
        x="arrival_date_month",
        y="bookings",
        color="hotel",
        markers=True
    )

    fig_hotel_monthly.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Month",
        yaxis_title="Bookings",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_hotel_monthly,
        use_container_width=True
    )

    # ========================================================
    # CHART 3 + 4
    # ========================================================

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # MONTHLY CANCELLATION RATE
    # --------------------------------------------------------

    with col1:

        st.markdown(
            '<div class="booking-trend-section">'
            '❌ Monthly Cancellation Rate'
            '</div>',
            unsafe_allow_html=True
        )

        fig_cancellation = px.line(
            monthly_data,
            x="arrival_date_month",
            y="cancellation_rate",
            markers=True
        )

        fig_cancellation.update_layout(
            height=400,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis_title="Month",
            yaxis_title="Cancellation Rate (%)",
            hovermode="x unified"
        )

        st.plotly_chart(
            fig_cancellation,
            use_container_width=True
        )

    # --------------------------------------------------------
    # MONTHLY ADR
    # --------------------------------------------------------

    with col2:

        st.markdown(
            '<div class="booking-trend-section">'
            '💰 Monthly ADR'
            '</div>',
            unsafe_allow_html=True
        )

        fig_monthly_adr = px.line(
            monthly_data,
            x="arrival_date_month",
            y="adr",
            markers=True
        )

        fig_monthly_adr.update_layout(
            height=400,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis_title="Month",
            yaxis_title="Average ADR",
            hovermode="x unified"
        )

        st.plotly_chart(
            fig_monthly_adr,
            use_container_width=True
        )

    # ========================================================
    # CHART 5 — MONTHLY REVENUE
    # ========================================================

    st.markdown(
        '<div class="booking-trend-section">'
        '💵 Monthly Estimated Revenue'
        '</div>',
        unsafe_allow_html=True
    )

    fig_revenue = px.bar(
        monthly_data,
        x="arrival_date_month",
        y="revenue",
        text="revenue"
    )

    fig_revenue.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside"
    )

    fig_revenue.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=40,
            t=20,
            b=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Month",
        yaxis_title="Estimated Revenue"
    )

    st.plotly_chart(
        fig_revenue,
        use_container_width=True
    )

    # ========================================================
    # CHART 6 + 7
    # ========================================================

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # BOOKINGS BY ARRIVAL DAY
    # --------------------------------------------------------

    with col1:

        st.markdown(
            '<div class="booking-trend-section">'
            '📆 Bookings by Arrival Day'
            '</div>',
            unsafe_allow_html=True
        )

        arrival_day = (
            data
            .groupby(
                "arrival_date_day_of_month"
            )
            .size()
            .reset_index(
                name="bookings"
            )
        )

        arrival_day = (
            arrival_day
            .sort_values(
                "arrival_date_day_of_month"
            )
        )

        fig_arrival_day = px.bar(
            arrival_day,
            x="arrival_date_day_of_month",
            y="bookings"
        )

        fig_arrival_day.update_layout(
            height=400,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis_title="Day of Month",
            yaxis_title="Bookings"
        )

        st.plotly_chart(
            fig_arrival_day,
            use_container_width=True
        )

    # --------------------------------------------------------
    # BOOKINGS BY WEEK NUMBER
    # --------------------------------------------------------

    with col2:

        st.markdown(
            '<div class="booking-trend-section">'
            '📅 Bookings by Week Number'
            '</div>',
            unsafe_allow_html=True
        )

        arrival_week = (
            data
            .groupby(
                "arrival_date_week_number"
            )
            .size()
            .reset_index(
                name="bookings"
            )
        )

        arrival_week = (
            arrival_week
            .sort_values(
                "arrival_date_week_number"
            )
        )

        fig_arrival_week = px.line(
            arrival_week,
            x="arrival_date_week_number",
            y="bookings",
            markers=True
        )

        fig_arrival_week.update_layout(
            height=400,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis_title="Arrival Week Number",
            yaxis_title="Bookings",
            hovermode="x unified"
        )

        st.plotly_chart(
            fig_arrival_week,
            use_container_width=True
        )

    # ========================================================
    # AUTOMATIC BUSINESS ANALYSIS
    # ========================================================

    st.markdown(
        '<div class="booking-trend-section">'
        '📌 Seasonal & Booking Insights'
        '</div>',
        unsafe_allow_html=True
    )

    insights = []

    # --------------------------------------------------------
    # Peak demand insight
    # --------------------------------------------------------

    peak_bookings = peak_booking_row["bookings"]

    insights.append(
        f"{peak_booking_month} records the highest booking "
        f"demand with approximately "
        f"{peak_bookings:,.0f} bookings."
    )

    # --------------------------------------------------------
    # Low demand insight
    # --------------------------------------------------------

    lowest_bookings = lowest_booking_row["bookings"]

    insights.append(
        f"{lowest_booking_month} has the lowest booking "
        f"volume with approximately "
        f"{lowest_bookings:,.0f} bookings, indicating a "
        f"potential low-demand period."
    )

    # --------------------------------------------------------
    # Seasonal demand
    # --------------------------------------------------------

    peak_avg = (
        monthly_data[
            monthly_data["arrival_date_month"]
            .isin(peak_season_months)
        ]["bookings"].mean()
    )

    overall_avg = monthly_data["bookings"].mean()

    if peak_avg > overall_avg:

        insights.append(
            f"The strongest demand is concentrated around "
            f"{peak_season}. These months perform above the "
            f"overall monthly booking average, indicating "
            f"a seasonal demand pattern."
        )

    # --------------------------------------------------------
    # Cancellation pattern
    # --------------------------------------------------------

    highest_cancel_row = (
        monthly_data
        .loc[
            monthly_data["cancellation_rate"].idxmax()
        ]
    )

    insights.append(
        f"{highest_cancel_row['arrival_date_month']} has the "
        f"highest monthly cancellation rate at "
        f"{highest_cancel_row['cancellation_rate']:.1f}%, "
        f"which may indicate increased booking risk during "
        f"this period."
    )

    # --------------------------------------------------------
    # Pricing pattern
    # --------------------------------------------------------

    highest_adr_row = (
        monthly_data
        .loc[
            monthly_data["adr"].idxmax()
        ]
    )

    insights.append(
        f"{highest_adr_row['arrival_date_month']} records the "
        f"highest average ADR at "
        f"{highest_adr_row['adr']:,.2f}, suggesting that "
        f"pricing increases during higher-value demand periods."
    )

    # --------------------------------------------------------
    # DISPLAY INSIGHTS
    # --------------------------------------------------------

    for i, insight in enumerate(
        insights[:5],
        start=1
    ):

        st.markdown(f"""
        <div class="booking-trend-insight">

            <div class="booking-trend-insight-title">
                📌 Insight {i}
            </div>

            <div class="booking-trend-insight-text">
                {insight}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # BUSINESS RECOMMENDATIONS
    # ========================================================

    st.markdown(
        '<div class="booking-trend-section">'
        '💡 Business Recommendations'
        '</div>',
        unsafe_allow_html=True
    )

    recommendations = []

    # --------------------------------------------------------
    # Peak season recommendation
    # --------------------------------------------------------

    recommendations.append((
        "🔥 Optimize Peak-Season Pricing",
        f"Increase pricing and protect room inventory during "
        f"the strongest demand months ({peak_season}). "
        "Dynamic pricing can help capture additional revenue "
        "without unnecessarily reducing availability."
    ))

    # --------------------------------------------------------
    # Low season recommendation
    # --------------------------------------------------------

    recommendations.append((
        "📉 Stimulate Low-Season Demand",
        f"{lowest_booking_month} shows the lowest booking "
        "volume. Consider targeted discounts, packages, "
        "promotional campaigns and partnerships during "
        "lower-demand periods."
    ))

    # --------------------------------------------------------
    # Cancellation recommendation
    # --------------------------------------------------------

    recommendations.append((
        "❌ Manage Seasonal Cancellation Risk",
        f"{highest_cancel_row['arrival_date_month']} has the "
        f"highest cancellation rate. Consider confirmation "
        "reminders, flexible but controlled cancellation "
        "policies and deposits for higher-risk bookings."
    ))

    # --------------------------------------------------------
    # Revenue recommendation
    # --------------------------------------------------------

    highest_revenue_row = (
        monthly_data
        .loc[
            monthly_data["revenue"].idxmax()
        ]
    )

    recommendations.append((
        "💰 Maximize High-Revenue Periods",
        f"{highest_revenue_row['arrival_date_month']} "
        f"generates the highest estimated revenue. "
        "Use demand forecasting and inventory optimization "
        "to maximize revenue during similar high-performing "
        "periods."
    ))

    # --------------------------------------------------------
    # DISPLAY RECOMMENDATIONS
    # --------------------------------------------------------

    for i, recommendation in enumerate(
        recommendations,
        start=1
    ):

        title, description = recommendation

        st.markdown(f"""
        <div class="booking-trend-recommendation">

            <div class="booking-trend-recommendation-title">
                💡 Recommendation {i} — {title}
            </div>

            <div class="booking-trend-recommendation-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

# ============================================================
# CANCELLATION ANALYSIS
# ============================================================

def render_cancellation_analysis(df):

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    if df is None or df.empty:
        st.warning("⚠️ No data available for cancellation analysis.")
        return

    data = df.copy()

    # --------------------------------------------------------
    # NUMERIC CONVERSION
    # --------------------------------------------------------

    numeric_columns = [
        "is_canceled",
        "lead_time",
        "adr",
        "stays_in_weekend_nights",
        "stays_in_weekdays_nights",
        "is_repeated_guest"
    ]

    for column in numeric_columns:

        if column in data.columns:
            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            )

    # --------------------------------------------------------
    # CALCULATED COLUMNS
    # --------------------------------------------------------

    data["total_stay_nights"] = (
        data["stays_in_weekend_nights"].fillna(0)
        +
        data["stays_in_weekdays_nights"].fillna(0)
    )

    data["estimated_revenue"] = (
        data["adr"].fillna(0)
        *
        data["total_stay_nights"]
    )

    # ========================================================
    # PAGE CSS
    # ========================================================

    st.markdown("""
    <style>

    /* ======================================================
       HEADER
       ====================================================== */

    .cancel-header {
        margin-top: 10px;
        margin-bottom: 25px;
    }

    .cancel-title {
        font-size: 32px;
        font-weight: 700;
        color: white;
        margin-bottom: 5px;
    }

    .cancel-subtitle {
        font-size: 14px;
        color: #9b9b9b;
    }

    /* ======================================================
       KPI CARDS
       ====================================================== */

    .cancel-kpi {

        background: rgba(20,20,20,0.90);

        border: 1px solid rgba(255,255,255,0.10);

        border-radius: 14px;

        padding: 18px;

        min-height: 110px;

        margin-bottom: 15px;

        box-shadow:
            0 7px 25px rgba(0,0,0,0.30),
            inset 0 0 18px rgba(255,255,255,0.015);

        transition: all 0.25s ease;
    }

    .cancel-kpi:hover {

        transform: translateY(-3px);

        border-color: rgba(32,255,138,0.35);

        box-shadow:
            0 8px 28px rgba(0,0,0,0.35),
            0 0 20px rgba(32,255,138,0.10);
    }

    .cancel-kpi-label {

        color: #999999;

        font-size: 11px;

        font-weight: 600;

        margin-bottom: 8px;
    }

    .cancel-kpi-value {

        color: white;

        font-size: 22px;

        font-weight: 700;
    }

    /* ======================================================
       SECTION
       ====================================================== */

    .cancel-section {

        color: white;

        font-size: 19px;

        font-weight: 700;

        margin-top: 28px;

        margin-bottom: 5px;
    }

    .cancel-description {

        color: #8d8d8d;

        font-size: 13px;

        margin-bottom: 15px;
    }

    /* ======================================================
       INSIGHT CARDS
       ====================================================== */

    .cancel-insight {

        background: rgba(4,35,20,0.82);

        border: 1px solid rgba(32,255,138,0.25);

        border-radius: 12px;

        padding: 15px 17px;

        margin-bottom: 10px;

        box-shadow:
            0 0 18px rgba(32,255,138,0.06);
    }

    .cancel-insight-title {

        color: #20ff8a;

        font-size: 14px;

        font-weight: 700;

        margin-bottom: 5px;
    }

    .cancel-insight-text {

        color: #d4d4d4;

        font-size: 13px;

        line-height: 1.5;
    }

    /* ======================================================
       RECOMMENDATION CARDS
       ====================================================== */

    .cancel-recommendation {

        background: rgba(20,20,20,0.92);

        border: 1px solid rgba(255,255,255,0.10);

        border-radius: 12px;

        padding: 16px 18px;

        margin-bottom: 10px;
    }

    .cancel-recommendation-title {

        color: white;

        font-size: 14px;

        font-weight: 700;

        margin-bottom: 5px;
    }

    .cancel-recommendation-text {

        color: #a5a5a5;

        font-size: 13px;

        line-height: 1.5;
    }

    </style>
    """, unsafe_allow_html=True)

    # ========================================================
    # PAGE HEADER
    # ========================================================

    st.markdown("""
    <div class="cancel-header">

        <div class="cancel-title">
            ❌ Cancellation Analysis
        </div>

        <div class="cancel-subtitle">
            Identify cancellation patterns, customer behaviour
            and the strongest drivers of booking cancellations.
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # KPI CALCULATIONS
    # ========================================================

    total_bookings = len(data)

    cancelled_bookings = (
        data["is_canceled"]
        .eq(1)
        .sum()
    )

    confirmed_bookings = (
        data["is_canceled"]
        .eq(0)
        .sum()
    )

    cancellation_rate = (
        cancelled_bookings
        /
        total_bookings
        *
        100
        if total_bookings > 0
        else 0
    )

    cancelled_data = data[
        data["is_canceled"] == 1
    ]

    revenue_lost = (
        cancelled_data["estimated_revenue"]
        .sum()
    )

    average_cancelled_lead_time = (
        cancelled_data["lead_time"].mean()
        if not cancelled_data.empty
        else 0
    )

    # ========================================================
    # KPI SECTION
    # ========================================================

    st.markdown(
        '<div class="cancel-section">'
        '📊 Cancellation KPIs'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="cancel-description">'
        'Overall cancellation performance and estimated '
        'financial impact.'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    # --------------------------------------------------------
    # TOTAL BOOKINGS
    # --------------------------------------------------------

    with col1:

        st.markdown(f"""
        <div class="cancel-kpi">

            <div class="cancel-kpi-label">
                TOTAL BOOKINGS
            </div>

            <div class="cancel-kpi-value">
                {total_bookings:,.0f}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # CANCELLED BOOKINGS
    # --------------------------------------------------------

    with col2:

        st.markdown(f"""
        <div class="cancel-kpi">

            <div class="cancel-kpi-label">
                ❌ CANCELLED BOOKINGS
            </div>

            <div class="cancel-kpi-value">
                {cancelled_bookings:,.0f}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # CONFIRMED BOOKINGS
    # --------------------------------------------------------

    with col3:

        st.markdown(f"""
        <div class="cancel-kpi">

            <div class="cancel-kpi-label">
                ✅ CONFIRMED BOOKINGS
            </div>

            <div class="cancel-kpi-value">
                {confirmed_bookings:,.0f}
            </div>

        </div>
        """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    # --------------------------------------------------------
    # CANCELLATION RATE
    # --------------------------------------------------------

    with col1:

        st.markdown(f"""
        <div class="cancel-kpi">

            <div class="cancel-kpi-label">
                CANCELLATION RATE
            </div>

            <div class="cancel-kpi-value">
                {cancellation_rate:.1f}%
            </div>

        </div>
        """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # REVENUE LOST
    # --------------------------------------------------------

    with col2:

        st.markdown(f"""
        <div class="cancel-kpi">

            <div class="cancel-kpi-label">
                💰 ESTIMATED REVENUE LOST
            </div>

            <div class="cancel-kpi-value">
                {revenue_lost:,.0f}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # AVERAGE LEAD TIME OF CANCELLED BOOKINGS
    # --------------------------------------------------------

    with col3:

        st.markdown(f"""
        <div class="cancel-kpi">

            <div class="cancel-kpi-label">
                ⏳ AVG LEAD TIME — CANCELLED
            </div>

            <div class="cancel-kpi-value">
                {average_cancelled_lead_time:.1f} days
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # CHART 1 — CANCELLATION BY HOTEL
    # ========================================================

    st.markdown(
        '<div class="cancel-section">'
        '🏨 Cancellation by Hotel'
        '</div>',
        unsafe_allow_html=True
    )

    hotel_cancel = (
        data
        .groupby("hotel")
        .agg(
            total_bookings=("hotel", "size"),
            cancelled=("is_canceled", "sum")
        )
        .reset_index()
    )

    hotel_cancel["cancellation_rate"] = (
        hotel_cancel["cancelled"]
        /
        hotel_cancel["total_bookings"]
        *
        100
    )

    fig_hotel_cancel = px.bar(
        hotel_cancel,
        x="hotel",
        y="cancellation_rate",
        text="cancellation_rate"
    )

    fig_hotel_cancel.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig_hotel_cancel.update_layout(
        height=400,
        margin=dict(
            l=20,
            r=40,
            t=20,
            b=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Hotel",
        yaxis_title="Cancellation Rate (%)"
    )

    st.plotly_chart(
        fig_hotel_cancel,
        use_container_width=True
    )

    # ========================================================
    # MONTH ORDER
    # ========================================================

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

    month_map = {
        month: index
        for index, month in enumerate(month_order)
    }

    # ========================================================
    # CHART 2 — CANCELLATION BY MONTH
    # ========================================================

    st.markdown(
        '<div class="cancel-section">'
        '📅 Cancellation by Month'
        '</div>',
        unsafe_allow_html=True
    )

    monthly_cancel = (
        data
        .groupby(
            "arrival_date_month",
            observed=False
        )
        .agg(
            bookings=("hotel", "size"),
            cancellations=("is_canceled", "sum")
        )
        .reset_index()
    )

    monthly_cancel["cancellation_rate"] = (
        monthly_cancel["cancellations"]
        /
        monthly_cancel["bookings"]
        *
        100
    )

    monthly_cancel["month_order"] = (
        monthly_cancel[
            "arrival_date_month"
        ].map(month_map)
    )

    monthly_cancel = (
        monthly_cancel
        .sort_values("month_order")
    )

    fig_month_cancel = px.line(
        monthly_cancel,
        x="arrival_date_month",
        y="cancellation_rate",
        markers=True
    )

    fig_month_cancel.update_layout(
        height=420,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Month",
        yaxis_title="Cancellation Rate (%)",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_month_cancel,
        use_container_width=True
    )

    # ========================================================
    # HELPER FUNCTION FOR CATEGORY ANALYSIS
    # ========================================================

    def category_cancellation_chart(
        dataframe,
        column,
        title,
        x_title
    ):

        category_data = (
            dataframe
            .groupby(column, dropna=False)
            .agg(
                total_bookings=("is_canceled", "size"),
                cancellations=("is_canceled", "sum")
            )
            .reset_index()
        )

        category_data["cancellation_rate"] = (
            category_data["cancellations"]
            /
            category_data["total_bookings"]
            *
            100
        )

        category_data = (
            category_data
            .sort_values(
                "cancellation_rate",
                ascending=False
            )
        )

        # Convert missing values to readable text

        category_data[column] = (
            category_data[column]
            .fillna("Unknown")
            .astype(str)
        )

        fig = px.bar(
            category_data,
            x=column,
            y="cancellation_rate",
            text="cancellation_rate"
        )

        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )

        fig.update_layout(
            height=420,
            margin=dict(
                l=20,
                r=40,
                t=20,
                b=70
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis_title=x_title,
            yaxis_title="Cancellation Rate (%)",
            xaxis_tickangle=-35
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        return category_data

    # ========================================================
    # MARKET SEGMENT + DISTRIBUTION CHANNEL
    # ========================================================

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            '<div class="cancel-section">'
            '🎯 Cancellation by Market Segment'
            '</div>',
            unsafe_allow_html=True
        )

        market_segment_data = category_cancellation_chart(
            data,
            "market_segment",
            "Cancellation by Market Segment",
            "Market Segment"
        )

    with col2:

        st.markdown(
            '<div class="cancel-section">'
            '📡 Cancellation by Distribution Channel'
            '</div>',
            unsafe_allow_html=True
        )

        distribution_data = category_cancellation_chart(
            data,
            "distribution_channel",
            "Cancellation by Distribution Channel",
            "Distribution Channel"
        )

    # ========================================================
    # DEPOSIT TYPE + CUSTOMER TYPE
    # ========================================================

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            '<div class="cancel-section">'
            '💳 Cancellation by Deposit Type'
            '</div>',
            unsafe_allow_html=True
        )

        deposit_data = category_cancellation_chart(
            data,
            "deposit_type",
            "Cancellation by Deposit Type",
            "Deposit Type"
        )

    with col2:

        st.markdown(
            '<div class="cancel-section">'
            '👤 Cancellation by Customer Type'
            '</div>',
            unsafe_allow_html=True
        )

        customer_data = category_cancellation_chart(
            data,
            "customer_type",
            "Cancellation by Customer Type",
            "Customer Type"
        )

    # ========================================================
    # REPEAT GUEST
    # ========================================================

    st.markdown(
        '<div class="cancel-section">'
        '🔁 Cancellation by Repeat Guest'
        '</div>',
        unsafe_allow_html=True
    )

    repeat_data = category_cancellation_chart(
        data,
        "is_repeated_guest",
        "Cancellation by Repeat Guest",
        "Repeat Guest"
    )

    # ========================================================
    # LEAD-TIME GROUP
    # ========================================================

    st.markdown(
        '<div class="cancel-section">'
        '⏳ Cancellation by Lead-Time Group'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # Create lead-time groups
    # --------------------------------------------------------

    lead_bins = [
        -1,
        30,
        60,
        90,
        180,
        float("inf")
    ]

    lead_labels = [
        "0–30 days",
        "31–60 days",
        "61–90 days",
        "91–180 days",
        "180+ days"
    ]

    data["lead_time_group"] = pd.cut(
        data["lead_time"],
        bins=lead_bins,
        labels=lead_labels
    )

    lead_time_data = (
        data
        .groupby(
            "lead_time_group",
            observed=False
        )
        .agg(
            total_bookings=("is_canceled", "size"),
            cancellations=("is_canceled", "sum")
        )
        .reset_index()
    )

    lead_time_data["cancellation_rate"] = (
        lead_time_data["cancellations"]
        /
        lead_time_data["total_bookings"]
        *
        100
    )

    fig_lead_cancel = px.bar(
        lead_time_data,
        x="lead_time_group",
        y="cancellation_rate",
        text="cancellation_rate"
    )

    fig_lead_cancel.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig_lead_cancel.update_layout(
        height=420,
        margin=dict(
            l=20,
            r=40,
            t=20,
            b=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Lead Time Group",
        yaxis_title="Cancellation Rate (%)"
    )

    st.plotly_chart(
        fig_lead_cancel,
        use_container_width=True
    )

    # ========================================================
    # STAY DURATION GROUP
    # ========================================================

    st.markdown(
        '<div class="cancel-section">'
        '🛏️ Cancellation by Stay Duration'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # Stay duration groups
    # --------------------------------------------------------

    stay_bins = [
        -1,
        1,
        3,
        5,
        7,
        14,
        float("inf")
    ]

    stay_labels = [
        "1 night",
        "2–3 nights",
        "4–5 nights",
        "6–7 nights",
        "8–14 nights",
        "15+ nights"
    ]

    data["stay_duration_group"] = pd.cut(
        data["total_stay_nights"],
        bins=stay_bins,
        labels=stay_labels
    )

    stay_data = (
        data
        .groupby(
            "stay_duration_group",
            observed=False
        )
        .agg(
            total_bookings=("is_canceled", "size"),
            cancellations=("is_canceled", "sum")
        )
        .reset_index()
    )

    stay_data["cancellation_rate"] = (
        stay_data["cancellations"]
        /
        stay_data["total_bookings"]
        *
        100
    )

    fig_stay_cancel = px.bar(
        stay_data,
        x="stay_duration_group",
        y="cancellation_rate",
        text="cancellation_rate"
    )

    fig_stay_cancel.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig_stay_cancel.update_layout(
        height=420,
        margin=dict(
            l=20,
            r=40,
            t=20,
            b=70
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Stay Duration",
        yaxis_title="Cancellation Rate (%)",
        xaxis_tickangle=-25
    )

    st.plotly_chart(
        fig_stay_cancel,
        use_container_width=True
    )

    # ========================================================
    # STRONGEST CANCELLATION DRIVERS
    # ========================================================

    st.markdown(
        '<div class="cancel-section">'
        '🔎 Strongest Cancellation Drivers'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="cancel-description">'
        'The following analysis compares cancellation rates '
        'across major booking characteristics.'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # Calculate strongest category for each dimension
    # --------------------------------------------------------

    driver_results = []

    # Hotel

    if not hotel_cancel.empty:

        row = hotel_cancel.loc[
            hotel_cancel["cancellation_rate"].idxmax()
        ]

        driver_results.append({
            "Factor": "Hotel Type",
            "Highest Risk Group": row["hotel"],
            "Cancellation Rate": row["cancellation_rate"]
        })

    # Market Segment

    if not market_segment_data.empty:

        row = market_segment_data.loc[
            market_segment_data["cancellation_rate"].idxmax()
        ]

        driver_results.append({
            "Factor": "Market Segment",
            "Highest Risk Group": row["market_segment"],
            "Cancellation Rate": row["cancellation_rate"]
        })

    # Distribution Channel

    if not distribution_data.empty:

        row = distribution_data.loc[
            distribution_data["cancellation_rate"].idxmax()
        ]

        driver_results.append({
            "Factor": "Distribution Channel",
            "Highest Risk Group": row["distribution_channel"],
            "Cancellation Rate": row["cancellation_rate"]
        })

    # Deposit Type

    if not deposit_data.empty:

        row = deposit_data.loc[
            deposit_data["cancellation_rate"].idxmax()
        ]

        driver_results.append({
            "Factor": "Deposit Type",
            "Highest Risk Group": row["deposit_type"],
            "Cancellation Rate": row["cancellation_rate"]
        })

    # Customer Type

    if not customer_data.empty:

        row = customer_data.loc[
            customer_data["cancellation_rate"].idxmax()
        ]

        driver_results.append({
            "Factor": "Customer Type",
            "Highest Risk Group": row["customer_type"],
            "Cancellation Rate": row["cancellation_rate"]
        })

    # Repeat Guest

    if not repeat_data.empty:

        row = repeat_data.loc[
            repeat_data["cancellation_rate"].idxmax()
        ]

        repeat_label = str(
            row["is_repeated_guest"]
        )

        if repeat_label == "1":
            repeat_label = "Repeat Guest"

        elif repeat_label == "0":
            repeat_label = "New Guest"

        driver_results.append({
            "Factor": "Guest Type",
            "Highest Risk Group": repeat_label,
            "Cancellation Rate": row["cancellation_rate"]
        })

    # Lead Time

    if not lead_time_data.empty:

        row = lead_time_data.loc[
            lead_time_data["cancellation_rate"].idxmax()
        ]

        driver_results.append({
            "Factor": "Lead Time",
            "Highest Risk Group": str(
                row["lead_time_group"]
            ),
            "Cancellation Rate": row["cancellation_rate"]
        })

    # Stay Duration

    if not stay_data.empty:

        row = stay_data.loc[
            stay_data["cancellation_rate"].idxmax()
        ]

        driver_results.append({
            "Factor": "Stay Duration",
            "Highest Risk Group": str(
                row["stay_duration_group"]
            ),
            "Cancellation Rate": row["cancellation_rate"]
        })

    # --------------------------------------------------------
    # Sort by cancellation rate
    # --------------------------------------------------------

    driver_results = sorted(
        driver_results,
        key=lambda x: x["Cancellation Rate"],
        reverse=True
    )

    # --------------------------------------------------------
    # Display strongest drivers
    # --------------------------------------------------------

    for i, driver in enumerate(
        driver_results[:5],
        start=1
    ):

        st.markdown(f"""
        <div class="cancel-insight">

            <div class="cancel-insight-title">
                🔥 Driver {i} — {driver['Factor']}
            </div>

            <div class="cancel-insight-text">
                <strong>{driver['Highest Risk Group']}</strong>
                records the highest cancellation rate within
                this factor at
                <strong>{driver['Cancellation Rate']:.1f}%</strong>.
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # BUSINESS INSIGHTS
    # ========================================================

    st.markdown(
        '<div class="cancel-section">'
        '📌 Cancellation Insights'
        '</div>',
        unsafe_allow_html=True
    )

    insights = []

    # Overall cancellation

    insights.append(
        f"The overall cancellation rate is "
        f"{cancellation_rate:.1f}%, with "
        f"{cancelled_bookings:,.0f} cancelled bookings out of "
        f"{total_bookings:,.0f} total bookings."
    )

    # Lead time

    if not lead_time_data.empty:

        highest_lead = lead_time_data.loc[
            lead_time_data["cancellation_rate"].idxmax()
        ]

        insights.append(
            f"Bookings in the "
            f"{highest_lead['lead_time_group']} lead-time group "
            f"have the highest cancellation rate at "
            f"{highest_lead['cancellation_rate']:.1f}%, "
            "highlighting lead time as an important potential "
            "cancellation indicator."
        )

    # Stay duration

    if not stay_data.empty:

        highest_stay = stay_data.loc[
            stay_data["cancellation_rate"].idxmax()
        ]

        insights.append(
            f"The "
            f"{highest_stay['stay_duration_group']} stay-duration "
            f"group has the highest cancellation rate at "
            f"{highest_stay['cancellation_rate']:.1f}%."
        )

    # Monthly cancellation

    highest_month = monthly_cancel.loc[
        monthly_cancel["cancellation_rate"].idxmax()
    ]

    insights.append(
        f"{highest_month['arrival_date_month']} records the "
        f"highest monthly cancellation rate at "
        f"{highest_month['cancellation_rate']:.1f}%."
    )

    # Revenue impact

    insights.append(
        f"Cancelled bookings represent an estimated revenue "
        f"impact of {revenue_lost:,.0f} based on ADR and "
        f"stay duration."
    )

    for i, insight in enumerate(
        insights,
        start=1
    ):

        st.markdown(f"""
        <div class="cancel-insight">

            <div class="cancel-insight-title">
                📌 Insight {i}
            </div>

            <div class="cancel-insight-text">
                {insight}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    st.markdown(
        '<div class="cancel-section">'
        '💡 Business Recommendations'
        '</div>',
        unsafe_allow_html=True
    )

    recommendations = []

    # --------------------------------------------------------
    # Lead time recommendation
    # --------------------------------------------------------

    if not lead_time_data.empty:

        highest_lead = lead_time_data.loc[
            lead_time_data["cancellation_rate"].idxmax()
        ]

        recommendations.append((
            "⏳ Target High-Risk Lead-Time Bookings",
            f"Bookings in the {highest_lead['lead_time_group']} "
            f"range have the highest cancellation rate. "
            "Consider stronger confirmation procedures, "
            "automated reminders or controlled deposits for "
            "high-risk reservations."
        ))

    # --------------------------------------------------------
    # Deposit recommendation
    # --------------------------------------------------------

    if not deposit_data.empty:

        highest_deposit = deposit_data.loc[
            deposit_data["cancellation_rate"].idxmax()
        ]

        recommendations.append((
            "💳 Strengthen Deposit Policies",
            f"{highest_deposit['deposit_type']} bookings show "
            f"the highest cancellation rate among deposit "
            "categories. Review deposit requirements and "
            "payment confirmation procedures for high-risk "
            "booking types."
        ))

    # --------------------------------------------------------
    # Market segment recommendation
    # --------------------------------------------------------

    if not market_segment_data.empty:

        highest_market = market_segment_data.loc[
            market_segment_data["cancellation_rate"].idxmax()
        ]

        recommendations.append((
            "🎯 Manage High-Risk Market Segments",
            f"The {highest_market['market_segment']} segment "
            f"has the highest cancellation rate at "
            f"{highest_market['cancellation_rate']:.1f}%. "
            "Review booking terms, pricing and cancellation "
            "policies for this customer segment."
        ))

    # --------------------------------------------------------
    # Seasonal recommendation
    # --------------------------------------------------------

    recommendations.append((
        "📅 Prepare for Seasonal Cancellation Risk",
        f"{highest_month['arrival_date_month']} has the "
        f"highest cancellation rate. Increase monitoring "
        "during high-risk months and use targeted reminders "
        "before arrival."
    ))

    # --------------------------------------------------------
    # Revenue protection
    # --------------------------------------------------------

    recommendations.append((
        "💰 Protect Revenue from Cancellations",
        f"Estimated revenue exposure from cancelled bookings "
        f"is {revenue_lost:,.0f}. Use demand forecasting, "
        "overbooking controls where appropriate and "
        "risk-based cancellation policies to reduce revenue "
        "loss."
    ))

    # --------------------------------------------------------
    # DISPLAY RECOMMENDATIONS
    # --------------------------------------------------------

    for i, recommendation in enumerate(
        recommendations[:5],
        start=1
    ):

        title, description = recommendation

        st.markdown(f"""
        <div class="cancel-recommendation">

            <div class="cancel-recommendation-title">
                💡 Recommendation {i} — {title}
            </div>

            <div class="cancel-recommendation-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

# ============================================================
# LEAD TIME ANALYSIS
# ============================================================

def render_lead_time_analysis(df):

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    if df is None or df.empty:
        st.warning("⚠️ No data available for lead time analysis.")
        return

    data = df.copy()

    # --------------------------------------------------------
    # NUMERIC CONVERSION
    # --------------------------------------------------------

    numeric_columns = [
        "lead_time",
        "is_canceled",
        "adr",
        "stays_in_weekend_nights",
        "stays_in_weekdays_nights"
    ]

    for column in numeric_columns:

        if column in data.columns:
            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            )

    # --------------------------------------------------------
    # CALCULATED COLUMNS
    # --------------------------------------------------------

    data["total_stay_nights"] = (
        data["stays_in_weekend_nights"].fillna(0)
        +
        data["stays_in_weekdays_nights"].fillna(0)
    )

    data["estimated_revenue"] = (
        data["adr"].fillna(0)
        *
        data["total_stay_nights"]
    )

    # Remove invalid lead-time values for lead-time analysis

    data = data[
        data["lead_time"].notna()
    ].copy()

    # ========================================================
    # PAGE CSS
    # ========================================================

    st.markdown("""
    <style>

    /* ======================================================
       HEADER
       ====================================================== */

    .lead-header {
        margin-top: 10px;
        margin-bottom: 25px;
    }

    .lead-title {
        font-size: 32px;
        font-weight: 700;
        color: white;
        margin-bottom: 5px;
    }

    .lead-subtitle {
        font-size: 14px;
        color: #9b9b9b;
    }

    /* ======================================================
       KPI CARDS
       ====================================================== */

    .lead-kpi {

        background: rgba(20,20,20,0.90);

        border: 1px solid rgba(255,255,255,0.10);

        border-radius: 14px;

        padding: 18px;

        min-height: 110px;

        margin-bottom: 15px;

        box-shadow:
            0 7px 25px rgba(0,0,0,0.30),
            inset 0 0 18px rgba(255,255,255,0.015);

        transition: all 0.25s ease;
    }

    .lead-kpi:hover {

        transform: translateY(-3px);

        border-color: rgba(32,255,138,0.35);

        box-shadow:
            0 8px 28px rgba(0,0,0,0.35),
            0 0 20px rgba(32,255,138,0.10);
    }

    .lead-kpi-label {

        color: #999999;

        font-size: 11px;

        font-weight: 600;

        margin-bottom: 8px;
    }

    .lead-kpi-value {

        color: white;

        font-size: 22px;

        font-weight: 700;
    }

    /* ======================================================
       SECTION
       ====================================================== */

    .lead-section {

        color: white;

        font-size: 19px;

        font-weight: 700;

        margin-top: 28px;

        margin-bottom: 5px;
    }

    .lead-description {

        color: #8d8d8d;

        font-size: 13px;

        margin-bottom: 15px;
    }

    /* ======================================================
       INSIGHT CARDS
       ====================================================== */

    .lead-insight {

        background: rgba(4,35,20,0.82);

        border: 1px solid rgba(32,255,138,0.25);

        border-radius: 12px;

        padding: 15px 17px;

        margin-bottom: 10px;

        box-shadow:
            0 0 18px rgba(32,255,138,0.06);
    }

    .lead-insight-title {

        color: #20ff8a;

        font-size: 14px;

        font-weight: 700;

        margin-bottom: 5px;
    }

    .lead-insight-text {

        color: #d4d4d4;

        font-size: 13px;

        line-height: 1.5;
    }

    /* ======================================================
       RECOMMENDATION CARDS
       ====================================================== */

    .lead-recommendation {

        background: rgba(20,20,20,0.92);

        border: 1px solid rgba(255,255,255,0.10);

        border-radius: 12px;

        padding: 16px 18px;

        margin-bottom: 10px;
    }

    .lead-recommendation-title {

        color: white;

        font-size: 14px;

        font-weight: 700;

        margin-bottom: 5px;
    }

    .lead-recommendation-text {

        color: #a5a5a5;

        font-size: 13px;

        line-height: 1.5;
    }

    </style>
    """, unsafe_allow_html=True)

    # ========================================================
    # HEADER
    # ========================================================

    st.markdown("""
    <div class="lead-header">

        <div class="lead-title">
            ⏳ Lead Time Analysis
        </div>

        <div class="lead-subtitle">
            Analyze how far in advance guests book, how lead
            time affects cancellations, pricing and revenue.
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # KPI CALCULATIONS
    # ========================================================

    average_lead_time = data["lead_time"].mean()

    median_lead_time = data["lead_time"].median()

    maximum_lead_time = data["lead_time"].max()

    minimum_lead_time = data["lead_time"].min()

    cancellation_rate = (
        data["is_canceled"].mean()
        *
        100
    )

    # ========================================================
    # KPI SECTION
    # ========================================================

    st.markdown(
        '<div class="lead-section">'
        '📊 Lead Time KPIs'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="lead-description">'
        'Summary statistics describing how far in advance '
        'hotel bookings are made.'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    # --------------------------------------------------------
    # AVERAGE
    # --------------------------------------------------------

    with col1:

        st.markdown(f"""
        <div class="lead-kpi">

            <div class="lead-kpi-label">
                📊 AVERAGE LEAD TIME
            </div>

            <div class="lead-kpi-value">
                {average_lead_time:.1f} days
            </div>

        </div>
        """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # MEDIAN
    # --------------------------------------------------------

    with col2:

        st.markdown(f"""
        <div class="lead-kpi">

            <div class="lead-kpi-label">
                📌 MEDIAN LEAD TIME
            </div>

            <div class="lead-kpi-value">
                {median_lead_time:.0f} days
            </div>

        </div>
        """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # MAXIMUM
    # --------------------------------------------------------

    with col3:

        st.markdown(f"""
        <div class="lead-kpi">

            <div class="lead-kpi-label">
                🔝 MAXIMUM LEAD TIME
            </div>

            <div class="lead-kpi-value">
                {maximum_lead_time:,.0f} days
            </div>

        </div>
        """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # MINIMUM
    # --------------------------------------------------------

    with col4:

        st.markdown(f"""
        <div class="lead-kpi">

            <div class="lead-kpi-label">
                🔽 MINIMUM LEAD TIME
            </div>

            <div class="lead-kpi-value">
                {minimum_lead_time:,.0f} days
            </div>

        </div>
        """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # CANCELLATION RATE
    # --------------------------------------------------------

    with col5:

        st.markdown(f"""
        <div class="lead-kpi">

            <div class="lead-kpi-label">
                ❌ CANCELLATION RATE
            </div>

            <div class="lead-kpi-value">
                {cancellation_rate:.1f}%
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # CHART 1 — LEAD TIME DISTRIBUTION
    # ========================================================

    st.markdown(
        '<div class="lead-section">'
        '📈 Lead Time Distribution'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="lead-description">'
        'Distribution of the number of days between booking '
        'and arrival.'
        '</div>',
        unsafe_allow_html=True
    )

    fig_distribution = px.histogram(
        data,
        x="lead_time",
        nbins=50
    )

    fig_distribution.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Lead Time (Days)",
        yaxis_title="Number of Bookings"
    )

    st.plotly_chart(
        fig_distribution,
        use_container_width=True
    )

    # ========================================================
    # CHART 2 — LEAD TIME BY HOTEL
    # ========================================================

    st.markdown(
        '<div class="lead-section">'
        '🏨 Lead Time by Hotel'
        '</div>',
        unsafe_allow_html=True
    )

    fig_hotel_box = px.box(
        data,
        x="hotel",
        y="lead_time",
        points=False
    )

    fig_hotel_box.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Hotel",
        yaxis_title="Lead Time (Days)"
    )

    st.plotly_chart(
        fig_hotel_box,
        use_container_width=True
    )

    # ========================================================
    # CREATE LEAD-TIME GROUPS
    # ========================================================

    lead_bins = [
        -1,
        7,
        30,
        60,
        90,
        180,
        float("inf")
    ]

    lead_labels = [
        "0–7 days",
        "8–30 days",
        "31–60 days",
        "61–90 days",
        "91–180 days",
        "180+ days"
    ]

    data["lead_time_group"] = pd.cut(
        data["lead_time"],
        bins=lead_bins,
        labels=lead_labels
    )

    # ========================================================
    # LEAD-TIME GROUP SUMMARY
    # ========================================================

    lead_group_summary = (
        data
        .groupby(
            "lead_time_group",
            observed=False
        )
        .agg(
            bookings=("lead_time", "size"),
            cancellation_rate=("is_canceled", "mean"),
            adr=("adr", "mean"),
            revenue=("estimated_revenue", "sum")
        )
        .reset_index()
    )

    lead_group_summary["cancellation_rate"] = (
        lead_group_summary["cancellation_rate"]
        *
        100
    )

    # ========================================================
    # LEAD-TIME GROUP TABLE
    # ========================================================

    st.markdown(
        '<div class="lead-section">'
        '📋 Lead-Time Group Performance'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="lead-description">'
        'Booking volume, cancellation rate, ADR and estimated '
        'revenue across lead-time groups.'
        '</div>',
        unsafe_allow_html=True
    )

    display_lead_summary = (
        lead_group_summary
        .copy()
    )

    display_lead_summary["cancellation_rate"] = (
        display_lead_summary["cancellation_rate"]
        .map(
            lambda x: f"{x:.1f}%"
        )
    )

    display_lead_summary["adr"] = (
        display_lead_summary["adr"]
        .map(
            lambda x: f"{x:,.2f}"
        )
    )

    display_lead_summary["revenue"] = (
        display_lead_summary["revenue"]
        .map(
            lambda x: f"{x:,.0f}"
        )
    )

    display_lead_summary.columns = [
        "Lead-Time Group",
        "Bookings",
        "Cancellation Rate",
        "Average ADR",
        "Estimated Revenue"
    ]

    st.dataframe(
        display_lead_summary,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # CHART 3 — LEAD TIME VS CANCELLATION
    # ========================================================

    st.markdown(
        '<div class="lead-section">'
        '❌ Lead Time vs Cancellation'
        '</div>',
        unsafe_allow_html=True
    )

    fig_lead_cancel = px.bar(
        lead_group_summary,
        x="lead_time_group",
        y="cancellation_rate",
        text="cancellation_rate"
    )

    fig_lead_cancel.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig_lead_cancel.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=40,
            t=20,
            b=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Lead-Time Group",
        yaxis_title="Cancellation Rate (%)"
    )

    st.plotly_chart(
        fig_lead_cancel,
        use_container_width=True
    )

    # ========================================================
    # CHART 4 — LEAD TIME BY MARKET SEGMENT
    # ========================================================

    st.markdown(
        '<div class="lead-section">'
        '🎯 Lead Time by Market Segment'
        '</div>',
        unsafe_allow_html=True
    )

    market_lead = (
        data
        .groupby(
            "market_segment",
            dropna=False
        )
        .agg(
            average_lead_time=("lead_time", "mean"),
            bookings=("lead_time", "size")
        )
        .reset_index()
    )

    market_lead["market_segment"] = (
        market_lead["market_segment"]
        .fillna("Unknown")
        .astype(str)
    )

    market_lead = (
        market_lead
        .sort_values(
            "average_lead_time",
            ascending=False
        )
    )

    fig_market_lead = px.bar(
        market_lead,
        x="market_segment",
        y="average_lead_time",
        text="average_lead_time"
    )

    fig_market_lead.update_traces(
        texttemplate="%{text:.1f} days",
        textposition="outside"
    )

    fig_market_lead.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=80
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Market Segment",
        yaxis_title="Average Lead Time (Days)",
        xaxis_tickangle=-35
    )

    st.plotly_chart(
        fig_market_lead,
        use_container_width=True
    )

    # ========================================================
    # CHART 5 — LEAD TIME BY CUSTOMER TYPE
    # ========================================================

    st.markdown(
        '<div class="lead-section">'
        '👤 Lead Time by Customer Type'
        '</div>',
        unsafe_allow_html=True
    )

    customer_lead = (
        data
        .groupby(
            "customer_type",
            dropna=False
        )
        .agg(
            average_lead_time=("lead_time", "mean"),
            bookings=("lead_time", "size")
        )
        .reset_index()
    )

    customer_lead["customer_type"] = (
        customer_lead["customer_type"]
        .fillna("Unknown")
        .astype(str)
    )

    customer_lead = (
        customer_lead
        .sort_values(
            "average_lead_time",
            ascending=False
        )
    )

    fig_customer_lead = px.bar(
        customer_lead,
        x="customer_type",
        y="average_lead_time",
        text="average_lead_time"
    )

    fig_customer_lead.update_traces(
        texttemplate="%{text:.1f} days",
        textposition="outside"
    )

    fig_customer_lead.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=80
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Customer Type",
        yaxis_title="Average Lead Time (Days)",
        xaxis_tickangle=-25
    )

    st.plotly_chart(
        fig_customer_lead,
        use_container_width=True
    )

    # ========================================================
    # CHART 6 — LEAD TIME VS ADR
    # ========================================================

    st.markdown(
        '<div class="lead-section">'
        '💰 Lead Time vs ADR'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="lead-description">'
        'Shows how average room pricing changes across '
        'different booking lead times.'
        '</div>',
        unsafe_allow_html=True
    )

    lead_adr = (
        data
        .groupby(
            "lead_time_group",
            observed=False
        )
        .agg(
            average_adr=("adr", "mean"),
            bookings=("adr", "size")
        )
        .reset_index()
    )

    fig_lead_adr = px.line(
        lead_adr,
        x="lead_time_group",
        y="average_adr",
        markers=True
    )

    fig_lead_adr.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Lead-Time Group",
        yaxis_title="Average ADR",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_lead_adr,
        use_container_width=True
    )

    # ========================================================
    # LEAD TIME VS REVENUE
    # ========================================================

    st.markdown(
        '<div class="lead-section">'
        '💵 Revenue by Lead-Time Group'
        '</div>',
        unsafe_allow_html=True
    )

    fig_lead_revenue = px.bar(
        lead_group_summary,
        x="lead_time_group",
        y="revenue",
        text="revenue"
    )

    fig_lead_revenue.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside"
    )

    fig_lead_revenue.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=40,
            t=20,
            b=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Lead-Time Group",
        yaxis_title="Estimated Revenue"
    )

    st.plotly_chart(
        fig_lead_revenue,
        use_container_width=True
    )

    # ========================================================
    # KEY ANALYSIS
    # ========================================================

    st.markdown(
        '<div class="lead-section">'
        '🔎 Lead Time & Cancellation Analysis'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # Highest cancellation group
    # --------------------------------------------------------

    highest_cancel_group = (
        lead_group_summary
        .loc[
            lead_group_summary[
                "cancellation_rate"
            ].idxmax()
        ]
    )

    lowest_cancel_group = (
        lead_group_summary
        .loc[
            lead_group_summary[
                "cancellation_rate"
            ].idxmin()
        ]
    )

    # --------------------------------------------------------
    # Determine trend
    # --------------------------------------------------------

    valid_groups = lead_group_summary[
        lead_group_summary["bookings"] > 0
    ].copy()

    if len(valid_groups) >= 2:

        first_rate = (
            valid_groups.iloc[0]["cancellation_rate"]
        )

        last_rate = (
            valid_groups.iloc[-1]["cancellation_rate"]
        )

        if last_rate > first_rate:

            trend_text = (
                "Cancellation rates generally increase "
                "as lead time becomes longer."
            )

        elif last_rate < first_rate:

            trend_text = (
                "Cancellation rates generally decrease "
                "as lead time becomes longer."
            )

        else:

            trend_text = (
                "Cancellation rates remain relatively stable "
                "across lead-time groups."
            )

    else:

        trend_text = (
            "There is not enough variation across lead-time "
            "groups to determine a reliable trend."
        )

    # --------------------------------------------------------
    # Display lead-time analysis
    # --------------------------------------------------------

    st.markdown(f"""
    <div class="lead-insight">

        <div class="lead-insight-title">
            📌 Cancellation Relationship
        </div>

        <div class="lead-insight-text">
            {trend_text}
        </div>

    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="lead-insight">

        <div class="lead-insight-title">
            🔥 Highest-Risk Lead-Time Group
        </div>

        <div class="lead-insight-text">
            The
            <strong>{highest_cancel_group['lead_time_group']}</strong>
            group has the highest cancellation rate at
            <strong>
                {highest_cancel_group['cancellation_rate']:.1f}%
            </strong>.
        </div>

    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="lead-insight">

        <div class="lead-insight-title">
            ✅ Lowest-Risk Lead-Time Group
        </div>

        <div class="lead-insight-text">
            The
            <strong>{lowest_cancel_group['lead_time_group']}</strong>
            group has the lowest cancellation rate at
            <strong>
                {lowest_cancel_group['cancellation_rate']:.1f}%
            </strong>.
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # BUSINESS INSIGHTS
    # ========================================================

    st.markdown(
        '<div class="lead-section">'
        '📌 Business Insights'
        '</div>',
        unsafe_allow_html=True
    )

    insights = []

    # Average vs median

    if average_lead_time > median_lead_time:

        insights.append(
            f"The average lead time of "
            f"{average_lead_time:.1f} days is higher than "
            f"the median of {median_lead_time:.0f} days, "
            "suggesting that a smaller number of very "
            "long-advance bookings are increasing the average."
        )

    else:

        insights.append(
            f"The average lead time is "
            f"{average_lead_time:.1f} days, while the median "
            f"is {median_lead_time:.0f} days, indicating that "
            "booking lead times are relatively concentrated "
            "around the central range."
        )

    # Highest cancellation

    insights.append(
        f"Bookings made within the "
        f"{highest_cancel_group['lead_time_group']} group "
        f"have the highest cancellation rate at "
        f"{highest_cancel_group['cancellation_rate']:.1f}%."
    )

    # Highest ADR

    highest_adr_group = (
        lead_group_summary
        .loc[
            lead_group_summary["adr"].idxmax()
        ]
    )

    insights.append(
        f"The "
        f"{highest_adr_group['lead_time_group']} group "
        f"records the highest average ADR at "
        f"{highest_adr_group['adr']:,.2f}."
    )

    # Highest revenue

    highest_revenue_group = (
        lead_group_summary
        .loc[
            lead_group_summary["revenue"].idxmax()
        ]
    )

    insights.append(
        f"The "
        f"{highest_revenue_group['lead_time_group']} group "
        f"generates the highest estimated revenue at "
        f"{highest_revenue_group['revenue']:,.0f}."
    )

    # Display

    for i, insight in enumerate(
        insights,
        start=1
    ):

        st.markdown(f"""
        <div class="lead-insight">

            <div class="lead-insight-title">
                📌 Insight {i}
            </div>

            <div class="lead-insight-text">
                {insight}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    st.markdown(
        '<div class="lead-section">'
        '💡 Business Recommendations'
        '</div>',
        unsafe_allow_html=True
    )

    recommendations = []

    # --------------------------------------------------------
    # High cancellation lead time
    # --------------------------------------------------------

    recommendations.append((
        "⏳ Manage High-Risk Advance Bookings",
        f"The {highest_cancel_group['lead_time_group']} "
        f"group has the highest cancellation rate. "
        "Consider stronger confirmation processes, "
        "pre-arrival reminders and appropriate deposit "
        "requirements for high-risk advance bookings."
    ))

    # --------------------------------------------------------
    # Pricing
    # --------------------------------------------------------

    recommendations.append((
        "💰 Use Lead Time for Dynamic Pricing",
        "Lead-time patterns can be incorporated into "
        "pricing strategies. Adjust ADR according to "
        "booking pace and expected demand instead of "
        "using a fixed room rate."
    ))

    # --------------------------------------------------------
    # Low lead-time bookings
    # --------------------------------------------------------

    recommendations.append((
        "📅 Capture Last-Minute Demand",
        "Monitor short lead-time bookings and maintain "
        "some inventory availability for last-minute "
        "customers, particularly during periods of "
        "strong demand."
    ))

    # --------------------------------------------------------
    # Revenue
    # --------------------------------------------------------

    recommendations.append((
        "📈 Optimize High-Value Lead-Time Segments",
        f"The {highest_revenue_group['lead_time_group']} "
        "group generates the highest estimated revenue. "
        "Use this segment's booking behaviour to improve "
        "inventory allocation and revenue forecasting."
    ))

    # --------------------------------------------------------
    # Display recommendations
    # --------------------------------------------------------

    for i, recommendation in enumerate(
        recommendations,
        start=1
    ):

        title, description = recommendation

        st.markdown(f"""
        <div class="lead-recommendation">

            <div class="lead-recommendation-title">
                💡 Recommendation {i} — {title}
            </div>

            <div class="lead-recommendation-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

# ============================================================
# STAY DURATION ANALYSIS
# ============================================================

def render_stay_duration_analysis(df):

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    if df is None or df.empty:
        st.warning("⚠️ No data available for stay duration analysis.")
        return

    data = df.copy()

    # --------------------------------------------------------
    # NUMERIC CONVERSION
    # --------------------------------------------------------

    numeric_columns = [
        "is_canceled",
        "adr",
        "stays_in_weekend_nights",
        "stays_in_weekdays_nights"
    ]

    for column in numeric_columns:

        if column in data.columns:
            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            )

    # --------------------------------------------------------
    # CREATE TOTAL STAY NIGHTS
    # --------------------------------------------------------

    data["stays_in_weekend_nights"] = (
        data["stays_in_weekend_nights"]
        .fillna(0)
    )

    data["stays_in_weekdays_nights"] = (
        data["stays_in_weekdays_nights"]
        .fillna(0)
    )

    data["total_stay_nights"] = (
        data["stays_in_weekend_nights"]
        +
        data["stays_in_weekdays_nights"]
    )

    # --------------------------------------------------------
    # ESTIMATED REVENUE
    # --------------------------------------------------------

    data["adr"] = data["adr"].fillna(0)

    data["estimated_revenue"] = (
        data["adr"]
        *
        data["total_stay_nights"]
    )

    # Remove invalid stay durations

    data = data[
        data["total_stay_nights"] > 0
    ].copy()

    if data.empty:
        st.warning(
            "⚠️ No valid stay-duration records are available."
        )
        return

    # ========================================================
    # PAGE CSS
    # ========================================================

    st.markdown("""
    <style>

    /* ======================================================
       HEADER
       ====================================================== */

    .stay-header {
        margin-top: 10px;
        margin-bottom: 25px;
    }

    .stay-title {
        font-size: 32px;
        font-weight: 700;
        color: white;
        margin-bottom: 5px;
    }

    .stay-subtitle {
        font-size: 14px;
        color: #9b9b9b;
    }

    /* ======================================================
       KPI CARDS
       ====================================================== */

    .stay-kpi {

        background: rgba(20,20,20,0.90);

        border: 1px solid rgba(255,255,255,0.10);

        border-radius: 14px;

        padding: 18px;

        min-height: 110px;

        margin-bottom: 15px;

        box-shadow:
            0 7px 25px rgba(0,0,0,0.30),
            inset 0 0 18px rgba(255,255,255,0.015);

        transition: all 0.25s ease;
    }

    .stay-kpi:hover {

        transform: translateY(-3px);

        border-color: rgba(32,255,138,0.35);

        box-shadow:
            0 8px 28px rgba(0,0,0,0.35),
            0 0 20px rgba(32,255,138,0.10);
    }

    .stay-kpi-label {

        color: #999999;

        font-size: 11px;

        font-weight: 600;

        margin-bottom: 8px;
    }

    .stay-kpi-value {

        color: white;

        font-size: 22px;

        font-weight: 700;
    }

    /* ======================================================
       SECTION
       ====================================================== */

    .stay-section {

        color: white;

        font-size: 19px;

        font-weight: 700;

        margin-top: 28px;

        margin-bottom: 5px;
    }

    .stay-description {

        color: #8d8d8d;

        font-size: 13px;

        margin-bottom: 15px;
    }

    /* ======================================================
       INSIGHT CARDS
       ====================================================== */

    .stay-insight {

        background: rgba(4,35,20,0.82);

        border: 1px solid rgba(32,255,138,0.25);

        border-radius: 12px;

        padding: 15px 17px;

        margin-bottom: 10px;

        box-shadow:
            0 0 18px rgba(32,255,138,0.06);
    }

    .stay-insight-title {

        color: #20ff8a;

        font-size: 14px;

        font-weight: 700;

        margin-bottom: 5px;
    }

    .stay-insight-text {

        color: #d4d4d4;

        font-size: 13px;

        line-height: 1.5;
    }

    /* ======================================================
       RECOMMENDATION CARDS
       ====================================================== */

    .stay-recommendation {

        background: rgba(20,20,20,0.92);

        border: 1px solid rgba(255,255,255,0.10);

        border-radius: 12px;

        padding: 16px 18px;

        margin-bottom: 10px;
    }

    .stay-recommendation-title {

        color: white;

        font-size: 14px;

        font-weight: 700;

        margin-bottom: 5px;
    }

    .stay-recommendation-text {

        color: #a5a5a5;

        font-size: 13px;

        line-height: 1.5;
    }

    </style>
    """, unsafe_allow_html=True)

    # ========================================================
    # HEADER
    # ========================================================

    st.markdown("""
    <div class="stay-header">

        <div class="stay-title">
            🛏 Stay Duration Analysis
        </div>

        <div class="stay-subtitle">
            Analyze how long guests stay and how stay duration
            affects cancellations, pricing and estimated revenue.
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # KPI CALCULATIONS
    # ========================================================

    average_stay = data["total_stay_nights"].mean()

    median_stay = data["total_stay_nights"].median()

    maximum_stay = data["total_stay_nights"].max()

    minimum_stay = data["total_stay_nights"].min()

    # Long stay = 8+ nights

    long_stay_percentage = (
        (
            data["total_stay_nights"] >= 8
        ).mean()
        *
        100
    )

    # ========================================================
    # KPI SECTION
    # ========================================================

    st.markdown(
        '<div class="stay-section">'
        '📊 Stay Duration KPIs'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="stay-description">'
        'Summary statistics describing the length of guest stays.'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    # --------------------------------------------------------
    # AVERAGE STAY
    # --------------------------------------------------------

    with col1:

        st.markdown(f"""
        <div class="stay-kpi">

            <div class="stay-kpi-label">
                📊 AVERAGE STAY
            </div>

            <div class="stay-kpi-value">
                {average_stay:.1f} nights
            </div>

        </div>
        """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # MEDIAN STAY
    # --------------------------------------------------------

    with col2:

        st.markdown(f"""
        <div class="stay-kpi">

            <div class="stay-kpi-label">
                📌 MEDIAN STAY
            </div>

            <div class="stay-kpi-value">
                {median_stay:.0f} nights
            </div>

        </div>
        """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # MAXIMUM STAY
    # --------------------------------------------------------

    with col3:

        st.markdown(f"""
        <div class="stay-kpi">

            <div class="stay-kpi-label">
                🔝 MAXIMUM STAY
            </div>

            <div class="stay-kpi-value">
                {maximum_stay:,.0f} nights
            </div>

        </div>
        """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # MINIMUM STAY
    # --------------------------------------------------------

    with col4:

        st.markdown(f"""
        <div class="stay-kpi">

            <div class="stay-kpi-label">
                🔽 MINIMUM STAY
            </div>

            <div class="stay-kpi-value">
                {minimum_stay:,.0f} nights
            </div>

        </div>
        """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # LONG-STAY %
    # --------------------------------------------------------

    with col5:

        st.markdown(f"""
        <div class="stay-kpi">

            <div class="stay-kpi-label">
                🛏 LONG-STAY BOOKINGS
            </div>

            <div class="stay-kpi-value">
                {long_stay_percentage:.1f}%
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # CHART 1 — STAY DURATION DISTRIBUTION
    # ========================================================

    st.markdown(
        '<div class="stay-section">'
        '📈 Stay Duration Distribution'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="stay-description">'
        'Distribution of total nights booked across all stays.'
        '</div>',
        unsafe_allow_html=True
    )

    fig_distribution = px.histogram(
        data,
        x="total_stay_nights",
        nbins=30
    )

    fig_distribution.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Total Stay (Nights)",
        yaxis_title="Number of Bookings"
    )

    st.plotly_chart(
        fig_distribution,
        use_container_width=True
    )

    # ========================================================
    # CHART 2 — STAY DURATION BY HOTEL
    # ========================================================

    st.markdown(
        '<div class="stay-section">'
        '🏨 Stay Duration by Hotel'
        '</div>',
        unsafe_allow_html=True
    )

    fig_hotel_box = px.box(
        data,
        x="hotel",
        y="total_stay_nights",
        points=False
    )

    fig_hotel_box.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Hotel",
        yaxis_title="Total Stay (Nights)"
    )

    st.plotly_chart(
        fig_hotel_box,
        use_container_width=True
    )

    # ========================================================
    # CREATE STAY GROUPS
    # ========================================================

    stay_bins = [
        0,
        1,
        3,
        7,
        14,
        float("inf")
    ]

    stay_labels = [
        "1 night",
        "2–3 nights",
        "4–7 nights",
        "8–14 nights",
        "15+ nights"
    ]

    data["stay_group"] = pd.cut(
        data["total_stay_nights"],
        bins=stay_bins,
        labels=stay_labels
    )

    # ========================================================
    # STAY GROUP SUMMARY
    # ========================================================

    stay_group_summary = (
        data
        .groupby(
            "stay_group",
            observed=False
        )
        .agg(
            bookings=("total_stay_nights", "size"),
            cancellation_rate=("is_canceled", "mean"),
            adr=("adr", "mean"),
            revenue=("estimated_revenue", "sum")
        )
        .reset_index()
    )

    stay_group_summary["cancellation_rate"] = (
        stay_group_summary["cancellation_rate"]
        *
        100
    )

    # ========================================================
    # STAY GROUP TABLE
    # ========================================================

    st.markdown(
        '<div class="stay-section">'
        '📋 Stay Group Performance'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="stay-description">'
        'Booking volume, cancellation rate, ADR and estimated '
        'revenue across different stay-duration groups.'
        '</div>',
        unsafe_allow_html=True
    )

    display_stay_summary = (
        stay_group_summary
        .copy()
    )

    display_stay_summary["cancellation_rate"] = (
        display_stay_summary["cancellation_rate"]
        .map(
            lambda x: f"{x:.1f}%"
        )
    )

    display_stay_summary["adr"] = (
        display_stay_summary["adr"]
        .map(
            lambda x: f"{x:,.2f}"
        )
    )

    display_stay_summary["revenue"] = (
        display_stay_summary["revenue"]
        .map(
            lambda x: f"{x:,.0f}"
        )
    )

    display_stay_summary.columns = [
        "Stay Group",
        "Bookings",
        "Cancellation Rate",
        "Average ADR",
        "Estimated Revenue"
    ]

    st.dataframe(
        display_stay_summary,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # CHART 3 — STAY DURATION VS CANCELLATION
    # ========================================================

    st.markdown(
        '<div class="stay-section">'
        '❌ Stay Duration vs Cancellation'
        '</div>',
        unsafe_allow_html=True
    )

    fig_stay_cancel = px.bar(
        stay_group_summary,
        x="stay_group",
        y="cancellation_rate",
        text="cancellation_rate"
    )

    fig_stay_cancel.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig_stay_cancel.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=40,
            t=20,
            b=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Stay Duration Group",
        yaxis_title="Cancellation Rate (%)"
    )

    st.plotly_chart(
        fig_stay_cancel,
        use_container_width=True
    )

    # ========================================================
    # CHART 4 — STAY DURATION BY CUSTOMER TYPE
    # ========================================================

    st.markdown(
        '<div class="stay-section">'
        '👤 Stay Duration by Customer Type'
        '</div>',
        unsafe_allow_html=True
    )

    customer_stay = (
        data
        .groupby(
            "customer_type",
            dropna=False
        )
        .agg(
            average_stay=("total_stay_nights", "mean"),
            bookings=("total_stay_nights", "size")
        )
        .reset_index()
    )

    customer_stay["customer_type"] = (
        customer_stay["customer_type"]
        .fillna("Unknown")
        .astype(str)
    )

    customer_stay = (
        customer_stay
        .sort_values(
            "average_stay",
            ascending=False
        )
    )

    fig_customer_stay = px.bar(
        customer_stay,
        x="customer_type",
        y="average_stay",
        text="average_stay"
    )

    fig_customer_stay.update_traces(
        texttemplate="%{text:.1f} nights",
        textposition="outside"
    )

    fig_customer_stay.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=80
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Customer Type",
        yaxis_title="Average Stay (Nights)",
        xaxis_tickangle=-25
    )

    st.plotly_chart(
        fig_customer_stay,
        use_container_width=True
    )

    # ========================================================
    # CHART 5 — STAY DURATION BY MARKET SEGMENT
    # ========================================================

    st.markdown(
        '<div class="stay-section">'
        '🎯 Stay Duration by Market Segment'
        '</div>',
        unsafe_allow_html=True
    )

    market_stay = (
        data
        .groupby(
            "market_segment",
            dropna=False
        )
        .agg(
            average_stay=("total_stay_nights", "mean"),
            bookings=("total_stay_nights", "size")
        )
        .reset_index()
    )

    market_stay["market_segment"] = (
        market_stay["market_segment"]
        .fillna("Unknown")
        .astype(str)
    )

    market_stay = (
        market_stay
        .sort_values(
            "average_stay",
            ascending=False
        )
    )

    fig_market_stay = px.bar(
        market_stay,
        x="market_segment",
        y="average_stay",
        text="average_stay"
    )

    fig_market_stay.update_traces(
        texttemplate="%{text:.1f} nights",
        textposition="outside"
    )

    fig_market_stay.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=90
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Market Segment",
        yaxis_title="Average Stay (Nights)",
        xaxis_tickangle=-35
    )

    st.plotly_chart(
        fig_market_stay,
        use_container_width=True
    )

    # ========================================================
    # CHART 6 — STAY DURATION VS ADR
    # ========================================================

    st.markdown(
        '<div class="stay-section">'
        '💰 Stay Duration vs ADR'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="stay-description">'
        'Shows how average room rates vary across different '
        'stay-duration groups.'
        '</div>',
        unsafe_allow_html=True
    )

    stay_adr = (
        data
        .groupby(
            "stay_group",
            observed=False
        )
        .agg(
            average_adr=("adr", "mean"),
            bookings=("adr", "size")
        )
        .reset_index()
    )

    fig_stay_adr = px.line(
        stay_adr,
        x="stay_group",
        y="average_adr",
        markers=True
    )

    fig_stay_adr.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Stay Duration Group",
        yaxis_title="Average ADR",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_stay_adr,
        use_container_width=True
    )

    # ========================================================
    # REVENUE BY STAY GROUP
    # ========================================================

    st.markdown(
        '<div class="stay-section">'
        '💵 Revenue by Stay Duration'
        '</div>',
        unsafe_allow_html=True
    )

    fig_stay_revenue = px.bar(
        stay_group_summary,
        x="stay_group",
        y="revenue",
        text="revenue"
    )

    fig_stay_revenue.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside"
    )

    fig_stay_revenue.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=40,
            t=20,
            b=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Stay Duration Group",
        yaxis_title="Estimated Revenue"
    )

    st.plotly_chart(
        fig_stay_revenue,
        use_container_width=True
    )

    # ========================================================
    # AUTOMATIC ANALYSIS
    # ========================================================

    st.markdown(
        '<div class="stay-section">'
        '🔎 Stay Duration Analysis'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # Highest cancellation group
    # --------------------------------------------------------

    highest_cancel_group = (
        stay_group_summary
        .loc[
            stay_group_summary[
                "cancellation_rate"
            ].idxmax()
        ]
    )

    # --------------------------------------------------------
    # Lowest cancellation group
    # --------------------------------------------------------

    lowest_cancel_group = (
        stay_group_summary
        .loc[
            stay_group_summary[
                "cancellation_rate"
            ].idxmin()
        ]
    )

    # --------------------------------------------------------
    # Longest average stay hotel
    # --------------------------------------------------------

    hotel_stay_summary = (
        data
        .groupby("hotel")
        ["total_stay_nights"]
        .mean()
        .sort_values(
            ascending=False
        )
    )

    longest_stay_hotel = (
        hotel_stay_summary
        .index[0]
    )

    longest_stay_hotel_value = (
        hotel_stay_summary
        .iloc[0]
    )

    # --------------------------------------------------------
    # Highest ADR group
    # --------------------------------------------------------

    highest_adr_group = (
        stay_group_summary
        .loc[
            stay_group_summary[
                "adr"
            ].idxmax()
        ]
    )

    # --------------------------------------------------------
    # Highest revenue group
    # --------------------------------------------------------

    highest_revenue_group = (
        stay_group_summary
        .loc[
            stay_group_summary[
                "revenue"
            ].idxmax()
        ]
    )

    # ========================================================
    # INSIGHTS
    # ========================================================

    insights = [

        (
            "📊 Typical Stay",
            f"The average guest stay is "
            f"{average_stay:.1f} nights, while the median "
            f"stay is {median_stay:.0f} nights."
        ),

        (
            "❌ Highest Cancellation Risk",
            f"The {highest_cancel_group['stay_group']} "
            f"stay group has the highest cancellation rate "
            f"at {highest_cancel_group['cancellation_rate']:.1f}%."
        ),

        (
            "🏨 Hotel Stay Pattern",
            f"{longest_stay_hotel} has the longest average "
            f"stay at {longest_stay_hotel_value:.1f} nights."
        ),

        (
            "💰 Highest ADR",
            f"The {highest_adr_group['stay_group']} group "
            f"has the highest average ADR at "
            f"{highest_adr_group['adr']:,.2f}."
        ),

        (
            "💵 Revenue Contribution",
            f"The {highest_revenue_group['stay_group']} "
            f"group generates the highest estimated revenue "
            f"at {highest_revenue_group['revenue']:,.0f}."
        )
    ]

    for i, insight in enumerate(
        insights,
        start=1
    ):

        title, description = insight

        st.markdown(f"""
        <div class="stay-insight">

            <div class="stay-insight-title">
                {title}
            </div>

            <div class="stay-insight-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # BUSINESS RECOMMENDATIONS
    # ========================================================

    st.markdown(
        '<div class="stay-section">'
        '💡 Business Recommendations'
        '</div>',
        unsafe_allow_html=True
    )

    recommendations = [

        (
            "🛏 Promote Longer Profitable Stays",
            "Use targeted packages and incentives to encourage "
            "guests to extend their stays when longer bookings "
            "generate stronger revenue."
        ),

        (
            "❌ Manage High-Risk Stay Groups",
            f"The {highest_cancel_group['stay_group']} group "
            f"has the highest cancellation rate. Consider "
            "stronger booking confirmation and deposit policies "
            "for this segment."
        ),

        (
            "💰 Use Stay Duration for Pricing",
            "Incorporate expected stay duration into revenue "
            "management and pricing decisions. Longer stays "
            "can be managed differently from short stays."
        ),

        (
            "📈 Optimize Inventory",
            "Use historical stay-duration patterns to improve "
            "room inventory planning and anticipate how many "
            "rooms will remain occupied over future periods."
        )
    ]

    for i, recommendation in enumerate(
        recommendations,
        start=1
    ):

        title, description = recommendation

        st.markdown(f"""
        <div class="stay-recommendation">

            <div class="stay-recommendation-title">
                💡 Recommendation {i} — {title}
            </div>

            <div class="stay-recommendation-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

# ============================================================
# REVENUE ANALYSIS
# ============================================================

def render_revenue_analysis(df):

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    if df is None or df.empty:
        st.warning("⚠️ No data available for revenue analysis.")
        return

    data = df.copy()

    # --------------------------------------------------------
    # REQUIRED NUMERIC COLUMNS
    # --------------------------------------------------------

    numeric_columns = [
        "is_canceled",
        "adr",
        "stays_in_weekend_nights",
        "stays_in_weekdays_nights"
    ]

    for column in numeric_columns:
        if column in data.columns:
            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            )

    # --------------------------------------------------------
    # FILL MISSING VALUES
    # --------------------------------------------------------

    data["adr"] = data["adr"].fillna(0)

    data["stays_in_weekend_nights"] = (
        data["stays_in_weekend_nights"].fillna(0)
    )

    data["stays_in_weekdays_nights"] = (
        data["stays_in_weekdays_nights"].fillna(0)
    )

    data["is_canceled"] = (
        data["is_canceled"].fillna(0)
    )

    # --------------------------------------------------------
    # CREATE TOTAL STAY NIGHTS
    # --------------------------------------------------------

    data["total_stay_nights"] = (
        data["stays_in_weekend_nights"]
        +
        data["stays_in_weekdays_nights"]
    )

    # --------------------------------------------------------
    # ESTIMATED REVENUE
    #
    # Estimated Revenue = ADR × Total Stay Nights
    # --------------------------------------------------------

    data["estimated_revenue"] = (
        data["adr"]
        *
        data["total_stay_nights"]
    )

    # --------------------------------------------------------
    # REVENUE LOST FROM CANCELLATIONS
    # --------------------------------------------------------

    data["revenue_lost"] = np.where(
        data["is_canceled"] == 1,
        data["estimated_revenue"],
        0
    )

    # --------------------------------------------------------
    # REMOVE INVALID ADR VALUES
    # --------------------------------------------------------

    data = data[
        data["adr"] >= 0
    ].copy()

    if data.empty:
        st.warning(
            "⚠️ No valid revenue records are available."
        )
        return

    # ========================================================
    # PAGE CSS
    # ========================================================

    st.markdown("""
    <style>

    /* ======================================================
       HEADER
       ====================================================== */

    .revenue-header {
        margin-top: 10px;
        margin-bottom: 25px;
    }

    .revenue-title {
        font-size: 32px;
        font-weight: 700;
        color: white;
        margin-bottom: 5px;
    }

    .revenue-subtitle {
        font-size: 14px;
        color: #9b9b9b;
    }

    /* ======================================================
       ESTIMATION NOTICE
       ====================================================== */

    .revenue-notice {

        background: rgba(35, 28, 4, 0.88);

        border: 1px solid rgba(255, 193, 7, 0.30);

        border-radius: 12px;

        padding: 14px 18px;

        margin-bottom: 22px;

        box-shadow:
            0 0 20px rgba(255,193,7,0.06);
    }

    .revenue-notice-title {

        color: #ffc107;

        font-weight: 700;

        font-size: 13px;

        margin-bottom: 4px;
    }

    .revenue-notice-text {

        color: #c8c8c8;

        font-size: 12px;

        line-height: 1.5;
    }

    /* ======================================================
       KPI CARDS
       ====================================================== */

    .revenue-kpi {

        background: rgba(20,20,20,0.90);

        border: 1px solid rgba(255,255,255,0.10);

        border-radius: 14px;

        padding: 18px;

        min-height: 110px;

        margin-bottom: 15px;

        box-shadow:
            0 7px 25px rgba(0,0,0,0.30),
            inset 0 0 18px rgba(255,255,255,0.015);

        transition: all 0.25s ease;
    }

    .revenue-kpi:hover {

        transform: translateY(-3px);

        border-color: rgba(32,255,138,0.35);

        box-shadow:
            0 8px 28px rgba(0,0,0,0.35),
            0 0 20px rgba(32,255,138,0.10);
    }

    .revenue-kpi-label {

        color: #999999;

        font-size: 11px;

        font-weight: 600;

        margin-bottom: 8px;
    }

    .revenue-kpi-value {

        color: white;

        font-size: 21px;

        font-weight: 700;
    }

    /* ======================================================
       SECTIONS
       ====================================================== */

    .revenue-section {

        color: white;

        font-size: 19px;

        font-weight: 700;

        margin-top: 28px;

        margin-bottom: 5px;
    }

    .revenue-description {

        color: #8d8d8d;

        font-size: 13px;

        margin-bottom: 15px;
    }

    /* ======================================================
       INSIGHTS
       ====================================================== */

    .revenue-insight {

        background: rgba(4,35,20,0.82);

        border: 1px solid rgba(32,255,138,0.25);

        border-radius: 12px;

        padding: 15px 17px;

        margin-bottom: 10px;

        box-shadow:
            0 0 18px rgba(32,255,138,0.06);
    }

    .revenue-insight-title {

        color: #20ff8a;

        font-size: 14px;

        font-weight: 700;

        margin-bottom: 5px;
    }

    .revenue-insight-text {

        color: #d4d4d4;

        font-size: 13px;

        line-height: 1.5;
    }

    /* ======================================================
       RECOMMENDATIONS
       ====================================================== */

    .revenue-recommendation {

        background: rgba(20,20,20,0.92);

        border: 1px solid rgba(255,255,255,0.10);

        border-radius: 12px;

        padding: 16px 18px;

        margin-bottom: 10px;
    }

    .revenue-recommendation-title {

        color: white;

        font-size: 14px;

        font-weight: 700;

        margin-bottom: 5px;
    }

    .revenue-recommendation-text {

        color: #a5a5a5;

        font-size: 13px;

        line-height: 1.5;
    }

    </style>
    """, unsafe_allow_html=True)

    # ========================================================
    # HEADER
    # ========================================================

    st.markdown("""
    <div class="revenue-header">

        <div class="revenue-title">
            💰 Revenue Analysis
        </div>

        <div class="revenue-subtitle">
            Analyze estimated revenue, room pricing,
            cancellation losses and revenue performance.
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # REVENUE NOTICE
    # ========================================================

    st.markdown("""
    <div class="revenue-notice">

        <div class="revenue-notice-title">
            ⚠️ Revenue Calculation Notice
        </div>

        <div class="revenue-notice-text">
            Revenue shown in this dashboard is estimated using
            ADR × Total Stay Nights. It represents an analytical
            approximation and should not be interpreted as actual
            collected revenue.
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # KPI CALCULATIONS
    # ========================================================

    total_revenue = data["estimated_revenue"].sum()

    average_adr = data["adr"].mean()

    median_adr = data["adr"].median()

    maximum_adr = data["adr"].max()

    city_revenue = data.loc[
        data["hotel"].astype(str).str.lower() == "city hotel",
        "estimated_revenue"
    ].sum()

    resort_revenue = data.loc[
        data["hotel"].astype(str).str.lower() == "resort hotel",
        "estimated_revenue"
    ].sum()

    revenue_lost = data.loc[
        data["is_canceled"] == 1,
        "estimated_revenue"
    ].sum()

    # ========================================================
    # KPI SECTION
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '📊 Revenue KPIs'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                💰 TOTAL ESTIMATED REVENUE
            </div>

            <div class="revenue-kpi-value">
                {total_revenue:,.0f}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                📊 AVERAGE ADR
            </div>

            <div class="revenue-kpi-value">
                {average_adr:,.2f}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                📌 MEDIAN ADR
            </div>

            <div class="revenue-kpi-value">
                {median_adr:,.2f}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                🔝 MAXIMUM ADR
            </div>

            <div class="revenue-kpi-value">
                {maximum_adr:,.2f}
            </div>

        </div>
        """, unsafe_allow_html=True)

    col5, col6, col7 = st.columns(3)

    with col5:
        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                🏨 CITY HOTEL REVENUE
            </div>

            <div class="revenue-kpi-value">
                {city_revenue:,.0f}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                🏝️ RESORT HOTEL REVENUE
            </div>

            <div class="revenue-kpi-value">
                {resort_revenue:,.0f}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col7:
        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                ❌ REVENUE LOST TO CANCELLATIONS
            </div>

            <div class="revenue-kpi-value">
                {revenue_lost:,.0f}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # 1. REVENUE BY HOTEL
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '🏨 Revenue by Hotel'
        '</div>',
        unsafe_allow_html=True
    )

    hotel_revenue = (
        data
        .groupby("hotel", dropna=False)
        .agg(
            revenue=("estimated_revenue", "sum"),
            bookings=("estimated_revenue", "size"),
            average_adr=("adr", "mean")
        )
        .reset_index()
    )

    hotel_revenue["hotel"] = (
        hotel_revenue["hotel"]
        .fillna("Unknown")
        .astype(str)
    )

    fig_hotel_revenue = px.bar(
        hotel_revenue,
        x="hotel",
        y="revenue",
        text="revenue"
    )

    fig_hotel_revenue.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside"
    )

    fig_hotel_revenue.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=40,
            t=20,
            b=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Hotel",
        yaxis_title="Estimated Revenue"
    )

    st.plotly_chart(
        fig_hotel_revenue,
        use_container_width=True
    )

    # ========================================================
    # CREATE MONTH NUMBER
    # ========================================================

    month_map = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12
    }

    if "arrival_date_month" in data.columns:

        data["month_number"] = (
            data["arrival_date_month"]
            .map(month_map)
        )

        data["arrival_date_month"] = (
            data["arrival_date_month"]
            .fillna("Unknown")
            .astype(str)
        )

    else:

        data["month_number"] = np.nan

    # ========================================================
    # 2. REVENUE BY MONTH
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '📅 Revenue by Month'
        '</div>',
        unsafe_allow_html=True
    )

    monthly_revenue = (
        data
        .groupby(
            ["month_number", "arrival_date_month"],
            dropna=False
        )
        .agg(
            revenue=("estimated_revenue", "sum")
        )
        .reset_index()
        .sort_values("month_number")
    )

    fig_month_revenue = px.line(
        monthly_revenue,
        x="arrival_date_month",
        y="revenue",
        markers=True
    )

    fig_month_revenue.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=30
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Month",
        yaxis_title="Estimated Revenue",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_month_revenue,
        use_container_width=True
    )

    # ========================================================
    # 3. REVENUE BY MARKET SEGMENT
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '🎯 Revenue by Market Segment'
        '</div>',
        unsafe_allow_html=True
    )

    market_revenue = (
        data
        .groupby(
            "market_segment",
            dropna=False
        )
        .agg(
            revenue=("estimated_revenue", "sum")
        )
        .reset_index()
        .sort_values(
            "revenue",
            ascending=False
        )
    )

    market_revenue["market_segment"] = (
        market_revenue["market_segment"]
        .fillna("Unknown")
        .astype(str)
    )

    fig_market_revenue = px.bar(
        market_revenue,
        x="market_segment",
        y="revenue",
        text="revenue"
    )

    fig_market_revenue.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside"
    )

    fig_market_revenue.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=100
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Market Segment",
        yaxis_title="Estimated Revenue",
        xaxis_tickangle=-35
    )

    st.plotly_chart(
        fig_market_revenue,
        use_container_width=True
    )

    # ========================================================
    # 4. ADR DISTRIBUTION
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '📈 ADR Distribution'
        '</div>',
        unsafe_allow_html=True
    )

    fig_adr_distribution = px.histogram(
        data,
        x="adr",
        nbins=40
    )

    fig_adr_distribution.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="ADR",
        yaxis_title="Number of Bookings"
    )

    st.plotly_chart(
        fig_adr_distribution,
        use_container_width=True
    )

    # ========================================================
    # 5. ADR BY HOTEL
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '🏨 ADR by Hotel'
        '</div>',
        unsafe_allow_html=True
    )

    hotel_adr = (
        data
        .groupby("hotel", dropna=False)
        .agg(
            average_adr=("adr", "mean")
        )
        .reset_index()
    )

    hotel_adr["hotel"] = (
        hotel_adr["hotel"]
        .fillna("Unknown")
        .astype(str)
    )

    fig_hotel_adr = px.bar(
        hotel_adr,
        x="hotel",
        y="average_adr",
        text="average_adr"
    )

    fig_hotel_adr.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_hotel_adr.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Hotel",
        yaxis_title="Average ADR"
    )

    st.plotly_chart(
        fig_hotel_adr,
        use_container_width=True
    )

    # ========================================================
    # 6. ADR BY MONTH
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '📅 ADR by Month'
        '</div>',
        unsafe_allow_html=True
    )

    monthly_adr = (
        data
        .groupby(
            ["month_number", "arrival_date_month"],
            dropna=False
        )
        .agg(
            average_adr=("adr", "mean")
        )
        .reset_index()
        .sort_values("month_number")
    )

    fig_month_adr = px.line(
        monthly_adr,
        x="arrival_date_month",
        y="average_adr",
        markers=True
    )

    fig_month_adr.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=30
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Month",
        yaxis_title="Average ADR",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_month_adr,
        use_container_width=True
    )

    # ========================================================
    # 7. REVENUE LOST BY CANCELLATION
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '❌ Revenue Lost to Cancellations'
        '</div>',
        unsafe_allow_html=True
    )

    cancellation_revenue = (
        data
        .groupby(
            "is_canceled"
        )
        .agg(
            revenue=("estimated_revenue", "sum")
        )
        .reset_index()
    )

    cancellation_revenue["status"] = (
        cancellation_revenue["is_canceled"]
        .map({
            0: "Confirmed",
            1: "Cancelled"
        })
    )

    fig_cancel_revenue = px.bar(
        cancellation_revenue,
        x="status",
        y="revenue",
        text="revenue"
    )

    fig_cancel_revenue.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside"
    )

    fig_cancel_revenue.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=40,
            t=20,
            b=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Booking Status",
        yaxis_title="Estimated Revenue"
    )

    st.plotly_chart(
        fig_cancel_revenue,
        use_container_width=True
    )

    # ========================================================
    # 8. ADR VS CANCELLATION
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '❌ ADR vs Cancellation'
        '</div>',
        unsafe_allow_html=True
    )

    adr_cancel = (
        data
        .groupby("is_canceled")
        .agg(
            average_adr=("adr", "mean"),
            bookings=("adr", "size")
        )
        .reset_index()
    )

    adr_cancel["status"] = (
        adr_cancel["is_canceled"]
        .map({
            0: "Confirmed",
            1: "Cancelled"
        })
    )

    fig_adr_cancel = px.bar(
        adr_cancel,
        x="status",
        y="average_adr",
        text="average_adr"
    )

    fig_adr_cancel.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_adr_cancel.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Booking Status",
        yaxis_title="Average ADR"
    )

    st.plotly_chart(
        fig_adr_cancel,
        use_container_width=True
    )

    # ========================================================
    # 9. REVENUE BY CUSTOMER TYPE
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '👤 Revenue by Customer Type'
        '</div>',
        unsafe_allow_html=True
    )

    customer_revenue = (
        data
        .groupby(
            "customer_type",
            dropna=False
        )
        .agg(
            revenue=("estimated_revenue", "sum")
        )
        .reset_index()
        .sort_values(
            "revenue",
            ascending=False
        )
    )

    customer_revenue["customer_type"] = (
        customer_revenue["customer_type"]
        .fillna("Unknown")
        .astype(str)
    )

    fig_customer_revenue = px.bar(
        customer_revenue,
        x="customer_type",
        y="revenue",
        text="revenue"
    )

    fig_customer_revenue.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside"
    )

    fig_customer_revenue.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=80
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Customer Type",
        yaxis_title="Estimated Revenue",
        xaxis_tickangle=-25
    )

    st.plotly_chart(
        fig_customer_revenue,
        use_container_width=True
    )

    # ========================================================
    # AUTOMATIC INSIGHTS
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '🔎 Revenue Insights'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # Highest revenue hotel
    # --------------------------------------------------------

    highest_revenue_hotel = (
        hotel_revenue
        .loc[
            hotel_revenue["revenue"].idxmax()
        ]
    )

    # --------------------------------------------------------
    # Highest ADR hotel
    # --------------------------------------------------------

    highest_adr_hotel = (
        hotel_adr
        .loc[
            hotel_adr["average_adr"].idxmax()
        ]
    )

    # --------------------------------------------------------
    # Highest revenue month
    # --------------------------------------------------------

    highest_revenue_month = (
        monthly_revenue
        .loc[
            monthly_revenue["revenue"].idxmax()
        ]
    )

    # --------------------------------------------------------
    # Highest revenue market
    # --------------------------------------------------------

    highest_revenue_market = (
        market_revenue
        .loc[
            market_revenue["revenue"].idxmax()
        ]
    )

    # --------------------------------------------------------
    # Cancellation revenue percentage
    # --------------------------------------------------------

    revenue_loss_percentage = (
        revenue_lost / total_revenue * 100
        if total_revenue > 0
        else 0
    )

    insights = [

        (
            "🏨 Top Revenue Generator",
            f"{highest_revenue_hotel['hotel']} generates the "
            f"highest estimated revenue at "
            f"{highest_revenue_hotel['revenue']:,.0f}."
        ),

        (
            "💰 Highest ADR",
            f"{highest_adr_hotel['hotel']} has the highest "
            f"average ADR at "
            f"{highest_adr_hotel['average_adr']:,.2f}."
        ),

        (
            "📅 Peak Revenue Month",
            f"{highest_revenue_month['arrival_date_month']} "
            f"generates the highest estimated monthly revenue "
            f"at {highest_revenue_month['revenue']:,.0f}."
        ),

        (
            "🎯 Leading Market Segment",
            f"{highest_revenue_market['market_segment']} "
            f"generates the highest estimated revenue among "
            f"market segments."
        ),

        (
            "❌ Cancellation Revenue Impact",
            f"Approximately {revenue_loss_percentage:.1f}% "
            f"of estimated revenue is associated with "
            f"cancelled bookings."
        )
    ]

    for title, description in insights:

        st.markdown(f"""
        <div class="revenue-insight">

            <div class="revenue-insight-title">
                {title}
            </div>

            <div class="revenue-insight-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # BUSINESS RECOMMENDATIONS
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '💡 Business Recommendations'
        '</div>',
        unsafe_allow_html=True
    )

    recommendations = [

        (
            "📈 Optimize Peak-Period Pricing",
            "Increase rates strategically during high-demand "
            "months while maintaining competitive pricing "
            "during low-demand periods."
        ),

        (
            "❌ Reduce Cancellation Revenue Loss",
            "Use deposits, flexible cancellation tiers and "
            "pre-arrival reminders to reduce revenue exposure "
            "from cancelled bookings."
        ),

        (
            "🏨 Apply Hotel-Specific Pricing",
            "Because City and Resort Hotels can have different "
            "ADR and revenue patterns, pricing strategies "
            "should be tailored to each property type."
        ),

        (
            "🎯 Focus on High-Value Segments",
            "Identify market and customer segments generating "
            "the strongest estimated revenue and develop "
            "targeted offers to increase their booking volume."
        )
    ]

    for i, recommendation in enumerate(
        recommendations,
        start=1
    ):

        title, description = recommendation

        st.markdown(f"""
        <div class="revenue-recommendation">

            <div class="revenue-recommendation-title">
                💡 Recommendation {i} — {title}
            </div>

            <div class="revenue-recommendation-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

# ============================================================
# 🌍 GEOGRAPHIC / MARKET ANALYSIS
# ============================================================

def render_geographic_market_analysis(df):

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    if df is None or df.empty:
        st.warning("⚠️ No data available for geographic analysis.")
        return

    data = df.copy()

    # --------------------------------------------------------
    # REQUIRED COLUMNS
    # --------------------------------------------------------

    if "is_canceled" in data.columns:
        data["is_canceled"] = pd.to_numeric(
            data["is_canceled"],
            errors="coerce"
        ).fillna(0)

    if "adr" in data.columns:
        data["adr"] = pd.to_numeric(
            data["adr"],
            errors="coerce"
        ).fillna(0)

    # --------------------------------------------------------
    # CREATE TOTAL STAY NIGHTS
    # --------------------------------------------------------

    if (
        "stays_in_weekend_nights" in data.columns
        and
        "stays_in_weekdays_nights" in data.columns
    ):

        data["total_stay_nights"] = (
            pd.to_numeric(
                data["stays_in_weekend_nights"],
                errors="coerce"
            ).fillna(0)
            +
            pd.to_numeric(
                data["stays_in_weekdays_nights"],
                errors="coerce"
            ).fillna(0)
        )

    else:
        data["total_stay_nights"] = 0

    # --------------------------------------------------------
    # ESTIMATED REVENUE
    # --------------------------------------------------------

    if "adr" in data.columns:

        data["estimated_revenue"] = (
            data["adr"]
            *
            data["total_stay_nights"]
        )

    else:

        data["estimated_revenue"] = 0

    # ========================================================
    # PAGE HEADER
    # ========================================================

    st.markdown("""
    <div class="revenue-header">

        <div class="revenue-title">
            🌍 Geographic & Market Analysis
        </div>

        <div class="revenue-subtitle">
            Analyze booking demand, cancellation behaviour,
            pricing and revenue across geographic and market segments.
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # 🌍 GEOGRAPHIC ANALYSIS
    # ========================================================

    if "country" in data.columns:

        st.markdown(
            '<div class="revenue-section">'
            '🌍 Geographic Analysis'
            '</div>',
            unsafe_allow_html=True
        )

        country_data = data.copy()

        country_data["country"] = (
            country_data["country"]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
        )

        # ----------------------------------------------------
        # REMOVE EMPTY COUNTRY VALUES
        # ----------------------------------------------------

        country_data.loc[
            country_data["country"] == "",
            "country"
        ] = "Unknown"

        # ----------------------------------------------------
        # GEOGRAPHIC KPIs
        # ----------------------------------------------------

        unique_countries = (
            country_data["country"]
            .nunique()
        )

        country_booking_counts = (
            country_data["country"]
            .value_counts()
        )

        if len(country_booking_counts) > 0:

            top_country = (
                country_booking_counts
                .idxmax()
            )

            top_country_bookings = (
                country_booking_counts
                .max()
            )

        else:

            top_country = "N/A"
            top_country_bookings = 0

        # ----------------------------------------------------
        # TOP 10 COUNTRY BOOKING VOLUME
        # ----------------------------------------------------

        top_10_countries = (
            country_booking_counts
            .head(10)
        )

        # ----------------------------------------------------
        # INTERNATIONAL BOOKING %
        #
        # Assumption:
        # The most frequent country is treated as the
        # domestic/home market.
        #
        # This is only an analytical proxy because the
        # dataset does not explicitly identify nationality.
        # ----------------------------------------------------

        if len(country_booking_counts) > 0:

            domestic_country = (
                country_booking_counts
                .idxmax()
            )

            international_bookings = (
                country_data["country"]
                != domestic_country
            ).sum()

            international_percentage = (
                international_bookings
                /
                len(country_data)
                *
                100
            )

        else:

            international_percentage = 0

        # ----------------------------------------------------
        # KPI CARDS
        # ----------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.markdown(f"""
            <div class="revenue-kpi">

                <div class="revenue-kpi-label">
                    🌍 UNIQUE COUNTRIES
                </div>

                <div class="revenue-kpi-value">
                    {unique_countries:,}
                </div>

            </div>
            """, unsafe_allow_html=True)

        with col2:

            st.markdown(f"""
            <div class="revenue-kpi">

                <div class="revenue-kpi-label">
                    🥇 TOP BOOKING COUNTRY
                </div>

                <div class="revenue-kpi-value">
                    {top_country}
                </div>

            </div>
            """, unsafe_allow_html=True)

        with col3:

            st.markdown(f"""
            <div class="revenue-kpi">

                <div class="revenue-kpi-label">
                    📊 TOP COUNTRY BOOKINGS
                </div>

                <div class="revenue-kpi-value">
                    {top_country_bookings:,}
                </div>

            </div>
            """, unsafe_allow_html=True)

        with col4:

            st.markdown(f"""
            <div class="revenue-kpi">

                <div class="revenue-kpi-label">
                    ✈️ INTERNATIONAL BOOKINGS
                </div>

                <div class="revenue-kpi-value">
                    {international_percentage:.1f}%
                </div>

            </div>
            """, unsafe_allow_html=True)

        # ====================================================
        # TOP 10 COUNTRIES
        # ====================================================

        st.markdown(
            '<div class="revenue-section">'
            '🌎 Top 10 Booking Countries'
            '</div>',
            unsafe_allow_html=True
        )

        top_country_df = (
            top_10_countries
            .reset_index()
        )

        top_country_df.columns = [
            "country",
            "bookings"
        ]

        fig_top_countries = px.bar(
            top_country_df,
            x="country",
            y="bookings",
            text="bookings"
        )

        fig_top_countries.update_traces(
            texttemplate="%{text:,}",
            textposition="outside"
        )

        fig_top_countries.update_layout(
            height=450,
            margin=dict(
                l=20,
                r=30,
                t=20,
                b=90
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis_title="Country",
            yaxis_title="Bookings",
            xaxis_tickangle=-35
        )

        st.plotly_chart(
            fig_top_countries,
            use_container_width=True
        )

        # ====================================================
        # COUNTRY CANCELLATION RATE
        # ====================================================

        st.markdown(
            '<div class="revenue-section">'
            '❌ Country Cancellation Rate'
            '</div>',
            unsafe_allow_html=True
        )

        country_cancel = (
            country_data
            .groupby("country")
            .agg(
                bookings=("is_canceled", "size"),
                cancellations=("is_canceled", "sum")
            )
            .reset_index()
        )

        country_cancel["cancellation_rate"] = (
            country_cancel["cancellations"]
            /
            country_cancel["bookings"]
            *
            100
        )

        # Only show countries with enough bookings
        country_cancel_chart = (
            country_cancel[
                country_cancel["bookings"] >= 20
            ]
            .sort_values(
                "cancellation_rate",
                ascending=False
            )
            .head(10)
        )

        if not country_cancel_chart.empty:

            fig_country_cancel = px.bar(
                country_cancel_chart,
                x="country",
                y="cancellation_rate",
                text="cancellation_rate"
            )

            fig_country_cancel.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside"
            )

            fig_country_cancel.update_layout(
                height=450,
                margin=dict(
                    l=20,
                    r=30,
                    t=20,
                    b=90
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                xaxis_title="Country",
                yaxis_title="Cancellation Rate (%)",
                xaxis_tickangle=-35
            )

            st.plotly_chart(
                fig_country_cancel,
                use_container_width=True
            )

        else:

            st.info(
                "Not enough country-level bookings "
                "to calculate reliable cancellation rates."
            )

        # ====================================================
        # COUNTRY REVENUE
        # ====================================================

        st.markdown(
            '<div class="revenue-section">'
            '💰 Country Revenue'
            '</div>',
            unsafe_allow_html=True
        )

        country_revenue = (
            country_data
            .groupby("country")
            .agg(
                revenue=("estimated_revenue", "sum")
            )
            .reset_index()
            .sort_values(
                "revenue",
                ascending=False
            )
            .head(10)
        )

        fig_country_revenue = px.bar(
            country_revenue,
            x="country",
            y="revenue",
            text="revenue"
        )

        fig_country_revenue.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside"
        )

        fig_country_revenue.update_layout(
            height=450,
            margin=dict(
                l=20,
                r=30,
                t=20,
                b=90
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis_title="Country",
            yaxis_title="Estimated Revenue",
            xaxis_tickangle=-35
        )

        st.plotly_chart(
            fig_country_revenue,
            use_container_width=True
        )

        # ====================================================
        # COUNTRY BOOKING VOLUME
        # ====================================================

        st.markdown(
            '<div class="revenue-section">'
            '📊 Country Booking Volume'
            '</div>',
            unsafe_allow_html=True
        )

        country_volume = (
            country_data
            .groupby("country")
            .size()
            .reset_index(
                name="bookings"
            )
            .sort_values(
                "bookings",
                ascending=False
            )
            .head(15)
        )

        fig_country_volume = px.bar(
            country_volume,
            x="country",
            y="bookings"
        )

        fig_country_volume.update_layout(
            height=450,
            margin=dict(
                l=20,
                r=30,
                t=20,
                b=100
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis_title="Country",
            yaxis_title="Booking Volume",
            xaxis_tickangle=-35
        )

        st.plotly_chart(
            fig_country_volume,
            use_container_width=True
        )

        # ====================================================
        # GEOGRAPHIC INSIGHT
        # ====================================================

        st.markdown(
            '<div class="revenue-section">'
            '🔎 Geographic Insights'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(f"""
        <div class="revenue-insight">

            <div class="revenue-insight-title">
                🌍 Market Concentration
            </div>

            <div class="revenue-insight-text">
                {top_country} is the largest booking market,
                accounting for {top_country_bookings:,}
                bookings in the dataset.
            </div>

        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="revenue-insight">

            <div class="revenue-insight-title">
                ✈️ International Demand
            </div>

            <div class="revenue-insight-text">
                Approximately {international_percentage:.1f}%
                of bookings come from countries other than
                the largest identified booking market.
            </div>

        </div>
        """, unsafe_allow_html=True)

    else:

        # ====================================================
        # COUNTRY NOT AVAILABLE
        # ====================================================

        st.markdown("""
        <div class="revenue-notice">

            <div class="revenue-notice-title">
                ℹ️ Geographic Analysis Not Available
            </div>

            <div class="revenue-notice-text">
                The uploaded dataset does not contain a
                <strong>country</strong> column.
                Geographic analysis has therefore been skipped.
                Market Segment Analysis is still available below.
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # 🎯 MARKET SEGMENT ANALYSIS
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '🎯 Market Segment Analysis'
        '</div>',
        unsafe_allow_html=True
    )

    if "market_segment" not in data.columns:

        st.warning(
            "⚠️ The uploaded dataset does not contain "
            "the market_segment column."
        )

        return

    market_data = data.copy()

    market_data["market_segment"] = (
        market_data["market_segment"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )

    market_data.loc[
        market_data["market_segment"] == "",
        "market_segment"
    ] = "Unknown"

    # ========================================================
    # MARKET SEGMENT KPIs
    # ========================================================

    unique_segments = (
        market_data["market_segment"]
        .nunique()
    )

    top_segment = (
        market_data["market_segment"]
        .value_counts()
        .idxmax()
    )

    top_segment_bookings = (
        market_data["market_segment"]
        .value_counts()
        .max()
    )

    market_total_revenue = (
        market_data["estimated_revenue"]
        .sum()
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                🎯 MARKET SEGMENTS
            </div>

            <div class="revenue-kpi-value">
                {unique_segments}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                🥇 TOP MARKET SEGMENT
            </div>

            <div class="revenue-kpi-value">
                {top_segment}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col3:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                📊 TOP SEGMENT BOOKINGS
            </div>

            <div class="revenue-kpi-value">
                {top_segment_bookings:,}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # 1. BOOKINGS BY MARKET SEGMENT
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '📊 Bookings by Market Segment'
        '</div>',
        unsafe_allow_html=True
    )

    segment_bookings = (
        market_data
        .groupby("market_segment")
        .size()
        .reset_index(
            name="bookings"
        )
        .sort_values(
            "bookings",
            ascending=False
        )
    )

    fig_segment_bookings = px.bar(
        segment_bookings,
        x="market_segment",
        y="bookings",
        text="bookings"
    )

    fig_segment_bookings.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig_segment_bookings.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=100
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Market Segment",
        yaxis_title="Bookings",
        xaxis_tickangle=-35
    )

    st.plotly_chart(
        fig_segment_bookings,
        use_container_width=True
    )

    # ========================================================
    # 2. CANCELLATION RATE BY MARKET SEGMENT
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '❌ Cancellation Rate by Market Segment'
        '</div>',
        unsafe_allow_html=True
    )

    segment_cancel = (
        market_data
        .groupby("market_segment")
        .agg(
            bookings=("is_canceled", "size"),
            cancellations=("is_canceled", "sum")
        )
        .reset_index()
    )

    segment_cancel["cancellation_rate"] = (
        segment_cancel["cancellations"]
        /
        segment_cancel["bookings"]
        *
        100
    )

    segment_cancel = segment_cancel.sort_values(
        "cancellation_rate",
        ascending=False
    )

    fig_segment_cancel = px.bar(
        segment_cancel,
        x="market_segment",
        y="cancellation_rate",
        text="cancellation_rate"
    )

    fig_segment_cancel.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig_segment_cancel.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=100
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Market Segment",
        yaxis_title="Cancellation Rate (%)",
        xaxis_tickangle=-35
    )

    st.plotly_chart(
        fig_segment_cancel,
        use_container_width=True
    )

    # ========================================================
    # 3. ADR BY MARKET SEGMENT
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '💵 ADR by Market Segment'
        '</div>',
        unsafe_allow_html=True
    )

    segment_adr = (
        market_data
        .groupby("market_segment")
        .agg(
            average_adr=("adr", "mean")
        )
        .reset_index()
        .sort_values(
            "average_adr",
            ascending=False
        )
    )

    fig_segment_adr = px.bar(
        segment_adr,
        x="market_segment",
        y="average_adr",
        text="average_adr"
    )

    fig_segment_adr.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_segment_adr.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=100
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Market Segment",
        yaxis_title="Average ADR",
        xaxis_tickangle=-35
    )

    st.plotly_chart(
        fig_segment_adr,
        use_container_width=True
    )

    # ========================================================
    # 4. REVENUE BY MARKET SEGMENT
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '💰 Revenue by Market Segment'
        '</div>',
        unsafe_allow_html=True
    )

    segment_revenue = (
        market_data
        .groupby("market_segment")
        .agg(
            revenue=("estimated_revenue", "sum")
        )
        .reset_index()
        .sort_values(
            "revenue",
            ascending=False
        )
    )

    fig_segment_revenue = px.bar(
        segment_revenue,
        x="market_segment",
        y="revenue",
        text="revenue"
    )

    fig_segment_revenue.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside"
    )

    fig_segment_revenue.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=100
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Market Segment",
        yaxis_title="Estimated Revenue",
        xaxis_tickangle=-35
    )

    st.plotly_chart(
        fig_segment_revenue,
        use_container_width=True
    )

    # ========================================================
    # MARKET SEGMENT INSIGHTS
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '🔎 Market Segment Insights'
        '</div>',
        unsafe_allow_html=True
    )

    highest_cancel_segment = (
        segment_cancel
        .loc[
            segment_cancel["cancellation_rate"].idxmax()
        ]
    )

    highest_adr_segment = (
        segment_adr
        .loc[
            segment_adr["average_adr"].idxmax()
        ]
    )

    highest_revenue_segment = (
        segment_revenue
        .loc[
            segment_revenue["revenue"].idxmax()
        ]
    )

    insights = [

        (
            "🎯 Dominant Market Segment",
            f"{top_segment} is the largest booking "
            f"segment with {top_segment_bookings:,} bookings."
        ),

        (
            "❌ Highest Cancellation Risk",
            f"{highest_cancel_segment['market_segment']} "
            f"has the highest cancellation rate at "
            f"{highest_cancel_segment['cancellation_rate']:.1f}%."
        ),

        (
            "💵 Highest ADR Segment",
            f"{highest_adr_segment['market_segment']} "
            f"has the highest average ADR at "
            f"{highest_adr_segment['average_adr']:.2f}."
        ),

        (
            "💰 Revenue Leader",
            f"{highest_revenue_segment['market_segment']} "
            f"generates the highest estimated revenue "
            f"among market segments."
        )
    ]

    for title, description in insights:

        st.markdown(f"""
        <div class="revenue-insight">

            <div class="revenue-insight-title">
                {title}
            </div>

            <div class="revenue-insight-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # MARKET RECOMMENDATIONS
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '💡 Market Recommendations'
        '</div>',
        unsafe_allow_html=True
    )

    recommendations = [

        (
            "🎯 Strengthen High-Volume Segments",
            f"Continue optimizing the {top_segment} "
            "segment because it represents the strongest "
            "booking volume."
        ),

        (
            "❌ Target High-Risk Segments",
            f"Review booking policies and cancellation "
            f"conditions for {highest_cancel_segment['market_segment']}, "
            "which shows the highest cancellation rate."
        ),

        (
            "💵 Optimize Segment Pricing",
            f"Use the pricing behaviour of "
            f"{highest_adr_segment['market_segment']} "
            "as a benchmark when developing segment-specific "
            "pricing strategies."
        ),

        (
            "📊 Diversify Demand",
            "Avoid relying too heavily on a single market "
            "segment by developing targeted campaigns for "
            "underperforming but potentially valuable segments."
        )
    ]

    for i, recommendation in enumerate(
        recommendations,
        start=1
    ):

        title, description = recommendation

        st.markdown(f"""
        <div class="revenue-recommendation">

            <div class="revenue-recommendation-title">
                💡 Recommendation {i} — {title}
            </div>

            <div class="revenue-recommendation-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

# ============================================================
# 📢 DISTRIBUTION CHANNEL ANALYSIS
# ============================================================

def render_distribution_channel_analysis(df):

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    if df is None or df.empty:
        st.warning("⚠️ No data available for distribution channel analysis.")
        return

    data = df.copy()

    # --------------------------------------------------------
    # REQUIRED COLUMN CHECK
    # --------------------------------------------------------

    required_columns = [
        "distribution_channel",
        "is_canceled",
        "adr"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing_columns:
        st.error(
            "❌ Required columns are missing: "
            + ", ".join(missing_columns)
        )
        return

    # --------------------------------------------------------
    # DATA TYPE CLEANING
    # --------------------------------------------------------

    data["is_canceled"] = pd.to_numeric(
        data["is_canceled"],
        errors="coerce"
    ).fillna(0)

    data["adr"] = pd.to_numeric(
        data["adr"],
        errors="coerce"
    ).fillna(0)

    # --------------------------------------------------------
    # CLEAN DISTRIBUTION CHANNEL
    # --------------------------------------------------------

    data["distribution_channel"] = (
        data["distribution_channel"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )

    data.loc[
        data["distribution_channel"] == "",
        "distribution_channel"
    ] = "Unknown"

    # --------------------------------------------------------
    # CREATE TOTAL STAY NIGHTS
    # --------------------------------------------------------

    if (
        "stays_in_weekend_nights" in data.columns
        and
        "stays_in_weekdays_nights" in data.columns
    ):

        data["total_stay_nights"] = (
            pd.to_numeric(
                data["stays_in_weekend_nights"],
                errors="coerce"
            ).fillna(0)
            +
            pd.to_numeric(
                data["stays_in_weekdays_nights"],
                errors="coerce"
            ).fillna(0)
        )

    else:

        data["total_stay_nights"] = 0

    # --------------------------------------------------------
    # ESTIMATED REVENUE
    # --------------------------------------------------------

    data["estimated_revenue"] = (
        data["adr"]
        *
        data["total_stay_nights"]
    )

    # ========================================================
    # PAGE HEADER
    # ========================================================

    st.markdown("""
    <div class="revenue-header">

        <div class="revenue-title">
            📢 Distribution Channel Analysis
        </div>

        <div class="revenue-subtitle">
            Analyze how customers reach the hotel and compare
            booking volume, cancellation risk, pricing and revenue
            across distribution channels.
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # CHANNEL SUMMARY
    # ========================================================

    channel_summary = (
        data
        .groupby("distribution_channel")
        .agg(
            bookings=("distribution_channel", "size"),
            cancellations=("is_canceled", "sum"),
            average_adr=("adr", "mean"),
            estimated_revenue=("estimated_revenue", "sum")
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # CANCELLATION RATE
    # --------------------------------------------------------

    channel_summary["cancellation_rate"] = (
        channel_summary["cancellations"]
        /
        channel_summary["bookings"]
        *
        100
    )

    # --------------------------------------------------------
    # BOOKING SHARE
    # --------------------------------------------------------

    total_bookings = len(data)

    channel_summary["booking_share"] = (
        channel_summary["bookings"]
        /
        total_bookings
        *
        100
    )

    # --------------------------------------------------------
    # SORTING
    # --------------------------------------------------------

    channel_summary = channel_summary.sort_values(
        "bookings",
        ascending=False
    )

    # ========================================================
    # KPI CALCULATIONS
    # ========================================================

    most_used_row = channel_summary.iloc[0]

    most_used_channel = (
        most_used_row["distribution_channel"]
    )

    most_used_bookings = int(
        most_used_row["bookings"]
    )

    most_used_share = (
        most_used_row["booking_share"]
    )

    highest_risk_row = channel_summary.loc[
        channel_summary["cancellation_rate"].idxmax()
    ]

    highest_risk_channel = (
        highest_risk_row["distribution_channel"]
    )

    highest_risk_rate = (
        highest_risk_row["cancellation_rate"]
    )

    highest_adr_row = channel_summary.loc[
        channel_summary["average_adr"].idxmax()
    ]

    highest_adr_channel = (
        highest_adr_row["distribution_channel"]
    )

    highest_adr = (
        highest_adr_row["average_adr"]
    )

    # ========================================================
    # KPI CARDS
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                📢 MOST USED CHANNEL
            </div>

            <div class="revenue-kpi-value">
                {most_used_channel}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                📊 CHANNEL BOOKING SHARE
            </div>

            <div class="revenue-kpi-value">
                {most_used_share:.1f}%
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col3:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                ❌ HIGHEST CANCELLATION RISK
            </div>

            <div class="revenue-kpi-value">
                {highest_risk_rate:.1f}%
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col4:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                💵 HIGHEST CHANNEL ADR
            </div>

            <div class="revenue-kpi-value">
                {highest_adr:.2f}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # 1. BOOKINGS BY DISTRIBUTION CHANNEL
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '📊 Bookings by Distribution Channel'
        '</div>',
        unsafe_allow_html=True
    )

    booking_chart = channel_summary.copy()

    fig_bookings = px.bar(
        booking_chart,
        x="distribution_channel",
        y="bookings",
        text="bookings"
    )

    fig_bookings.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig_bookings.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=80
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Distribution Channel",
        yaxis_title="Bookings",
        xaxis_tickangle=-25
    )

    st.plotly_chart(
        fig_bookings,
        use_container_width=True
    )

    # ========================================================
    # 2. CANCELLATION RATE BY CHANNEL
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '❌ Cancellation Rate by Channel'
        '</div>',
        unsafe_allow_html=True
    )

    cancellation_chart = channel_summary.sort_values(
        "cancellation_rate",
        ascending=False
    )

    fig_cancellation = px.bar(
        cancellation_chart,
        x="distribution_channel",
        y="cancellation_rate",
        text="cancellation_rate"
    )

    fig_cancellation.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig_cancellation.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=80
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Distribution Channel",
        yaxis_title="Cancellation Rate (%)",
        xaxis_tickangle=-25
    )

    st.plotly_chart(
        fig_cancellation,
        use_container_width=True
    )

    # ========================================================
    # 3. ADR BY CHANNEL
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '💵 ADR by Distribution Channel'
        '</div>',
        unsafe_allow_html=True
    )

    adr_chart = channel_summary.sort_values(
        "average_adr",
        ascending=False
    )

    fig_adr = px.bar(
        adr_chart,
        x="distribution_channel",
        y="average_adr",
        text="average_adr"
    )

    fig_adr.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_adr.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=80
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Distribution Channel",
        yaxis_title="Average ADR",
        xaxis_tickangle=-25
    )

    st.plotly_chart(
        fig_adr,
        use_container_width=True
    )

    # ========================================================
    # 4. REVENUE BY CHANNEL
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '💰 Revenue by Distribution Channel'
        '</div>',
        unsafe_allow_html=True
    )

    revenue_chart = channel_summary.sort_values(
        "estimated_revenue",
        ascending=False
    )

    fig_revenue = px.bar(
        revenue_chart,
        x="distribution_channel",
        y="estimated_revenue",
        text="estimated_revenue"
    )

    fig_revenue.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside"
    )

    fig_revenue.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=80
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Distribution Channel",
        yaxis_title="Estimated Revenue",
        xaxis_tickangle=-25
    )

    st.plotly_chart(
        fig_revenue,
        use_container_width=True
    )

    # ========================================================
    # CHANNEL PERFORMANCE TABLE
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '📋 Channel Performance Summary'
        '</div>',
        unsafe_allow_html=True
    )

    display_table = channel_summary.copy()

    display_table = display_table[
        [
            "distribution_channel",
            "bookings",
            "booking_share",
            "cancellation_rate",
            "average_adr",
            "estimated_revenue"
        ]
    ]

    display_table.columns = [
        "Distribution Channel",
        "Bookings",
        "Booking Share %",
        "Cancellation Rate %",
        "Average ADR",
        "Estimated Revenue"
    ]

    display_table["Booking Share %"] = (
        display_table["Booking Share %"]
        .round(2)
    )

    display_table["Cancellation Rate %"] = (
        display_table["Cancellation Rate %"]
        .round(2)
    )

    display_table["Average ADR"] = (
        display_table["Average ADR"]
        .round(2)
    )

    display_table["Estimated Revenue"] = (
        display_table["Estimated Revenue"]
        .round(2)
    )

    st.dataframe(
        display_table,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # 🔎 BUSINESS INSIGHTS
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '🔎 Distribution Channel Insights'
        '</div>',
        unsafe_allow_html=True
    )

    highest_revenue_row = channel_summary.loc[
        channel_summary["estimated_revenue"].idxmax()
    ]

    highest_revenue_channel = (
        highest_revenue_row["distribution_channel"]
    )

    highest_revenue = (
        highest_revenue_row["estimated_revenue"]
    )

    insights = [

        (
            "📢 Volume Leader",
            f"{most_used_channel} is the most frequently "
            f"used distribution channel, generating "
            f"{most_used_bookings:,} bookings "
            f"({most_used_share:.1f}% of all bookings)."
        ),

        (
            "❌ Cancellation Risk",
            f"{highest_risk_channel} has the highest "
            f"cancellation rate at "
            f"{highest_risk_rate:.1f}%."
        ),

        (
            "💵 Pricing Leader",
            f"{highest_adr_channel} produces the highest "
            f"average ADR at {highest_adr:.2f}."
        ),

        (
            "💰 Revenue Leader",
            f"{highest_revenue_channel} generates the "
            f"highest estimated revenue of "
            f"{highest_revenue:,.0f}."
        )
    ]

    for title, description in insights:

        st.markdown(f"""
        <div class="revenue-insight">

            <div class="revenue-insight-title">
                {title}
            </div>

            <div class="revenue-insight-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # 💡 RECOMMENDATIONS
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '💡 Distribution Channel Recommendations'
        '</div>',
        unsafe_allow_html=True
    )

    recommendations = [

        (
            "Optimize the dominant channel",
            f"{most_used_channel} generates the largest "
            "booking volume. Maintain strong availability "
            "and visibility on this channel while monitoring "
            "its profitability."
        ),

        (
            "Reduce cancellation exposure",
            f"Review cancellation policies and booking "
            f"conditions for {highest_risk_channel}, "
            "which has the highest cancellation rate."
        ),

        (
            "Leverage high-value channels",
            f"{highest_adr_channel} produces the highest "
            "ADR. Consider targeted promotions and premium "
            "offers to attract more customers through this channel."
        ),

        (
            "Balance volume and profitability",
            "The channel with the most bookings is not "
            "necessarily the most profitable. Evaluate "
            "booking volume, ADR, cancellation rate and "
            "estimated revenue together when allocating "
            "marketing resources."
        )
    ]

    for i, recommendation in enumerate(
        recommendations,
        start=1
    ):

        title, description = recommendation

        st.markdown(f"""
        <div class="revenue-recommendation">

            <div class="revenue-recommendation-title">
                💡 Recommendation {i} — {title}
            </div>

            <div class="revenue-recommendation-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

# ============================================================
# 👥 CUSTOMER ANALYSIS
# ============================================================

def render_customer_analysis(df):

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    if df is None or df.empty:
        st.warning("⚠️ No data available for customer analysis.")
        return

    data = df.copy()

    # --------------------------------------------------------
    # REQUIRED COLUMN CHECK
    # --------------------------------------------------------

    required_columns = [
        "customer_type",
        "is_canceled",
        "adr"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing_columns:
        st.error(
            "❌ Required columns are missing: "
            + ", ".join(missing_columns)
        )
        return

    # --------------------------------------------------------
    # DATA TYPE CONVERSION
    # --------------------------------------------------------

    data["is_canceled"] = pd.to_numeric(
        data["is_canceled"],
        errors="coerce"
    ).fillna(0)

    data["adr"] = pd.to_numeric(
        data["adr"],
        errors="coerce"
    ).fillna(0)

    # --------------------------------------------------------
    # CLEAN CUSTOMER TYPE
    # --------------------------------------------------------

    data["customer_type"] = (
        data["customer_type"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )

    data.loc[
        data["customer_type"] == "",
        "customer_type"
    ] = "Unknown"

    # ========================================================
    # CREATE TOTAL STAY NIGHTS
    # ========================================================

    if (
        "stays_in_weekend_nights" in data.columns
        and
        "stays_in_weekdays_nights" in data.columns
    ):

        data["total_stay_nights"] = (
            pd.to_numeric(
                data["stays_in_weekend_nights"],
                errors="coerce"
            ).fillna(0)
            +
            pd.to_numeric(
                data["stays_in_weekdays_nights"],
                errors="coerce"
            ).fillna(0)
        )

    else:

        data["total_stay_nights"] = 0

    # --------------------------------------------------------
    # ESTIMATED REVENUE
    # --------------------------------------------------------

    data["estimated_revenue"] = (
        data["adr"]
        *
        data["total_stay_nights"]
    )

    # ========================================================
    # PAGE HEADER
    # ========================================================

    st.markdown("""
    <div class="revenue-header">

        <div class="revenue-title">
            👥 Customer Analysis
        </div>

        <div class="revenue-subtitle">
            Analyze customer behaviour, booking patterns,
            cancellation risk, pricing and stay duration
            across different customer types.
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # CUSTOMER SUMMARY
    # ========================================================

    customer_summary = (
        data
        .groupby("customer_type")
        .agg(
            bookings=("customer_type", "size"),
            cancellations=("is_canceled", "sum"),
            average_adr=("adr", "mean"),
            average_stay=("total_stay_nights", "mean"),
            estimated_revenue=("estimated_revenue", "sum")
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # CANCELLATION RATE
    # --------------------------------------------------------

    customer_summary["cancellation_rate"] = (
        customer_summary["cancellations"]
        /
        customer_summary["bookings"]
        *
        100
    )

    # --------------------------------------------------------
    # BOOKING SHARE
    # --------------------------------------------------------

    total_bookings = len(data)

    customer_summary["booking_share"] = (
        customer_summary["bookings"]
        /
        total_bookings
        *
        100
    )

    customer_summary = customer_summary.sort_values(
        "bookings",
        ascending=False
    )

    # ========================================================
    # KPI CALCULATIONS
    # ========================================================

    total_customer_types = (
        customer_summary["customer_type"]
        .nunique()
    )

    most_common_row = customer_summary.iloc[0]

    most_common_type = (
        most_common_row["customer_type"]
    )

    most_common_bookings = int(
        most_common_row["bookings"]
    )

    highest_cancel_row = customer_summary.loc[
        customer_summary["cancellation_rate"].idxmax()
    ]

    highest_cancel_type = (
        highest_cancel_row["customer_type"]
    )

    highest_cancel_rate = (
        highest_cancel_row["cancellation_rate"]
    )

    highest_adr_row = customer_summary.loc[
        customer_summary["average_adr"].idxmax()
    ]

    highest_adr_type = (
        highest_adr_row["customer_type"]
    )

    highest_adr = (
        highest_adr_row["average_adr"]
    )

    # ========================================================
    # KPI CARDS
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                👥 CUSTOMER TYPES
            </div>

            <div class="revenue-kpi-value">
                {total_customer_types}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                🥇 MOST COMMON CUSTOMER
            </div>

            <div class="revenue-kpi-value">
                {most_common_type}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col3:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                ❌ HIGHEST CANCELLATION
            </div>

            <div class="revenue-kpi-value">
                {highest_cancel_rate:.1f}%
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col4:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                💵 HIGHEST CUSTOMER ADR
            </div>

            <div class="revenue-kpi-value">
                {highest_adr:.2f}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # 1. BOOKINGS BY CUSTOMER TYPE
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '📊 Bookings by Customer Type'
        '</div>',
        unsafe_allow_html=True
    )

    booking_chart = customer_summary.copy()

    fig_bookings = px.bar(
        booking_chart,
        x="customer_type",
        y="bookings",
        text="bookings"
    )

    fig_bookings.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig_bookings.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=80
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Customer Type",
        yaxis_title="Bookings",
        xaxis_tickangle=-20
    )

    st.plotly_chart(
        fig_bookings,
        use_container_width=True
    )

    # ========================================================
    # 2. CANCELLATION BY CUSTOMER TYPE
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '❌ Cancellation Rate by Customer Type'
        '</div>',
        unsafe_allow_html=True
    )

    cancellation_chart = customer_summary.sort_values(
        "cancellation_rate",
        ascending=False
    )

    fig_cancellation = px.bar(
        cancellation_chart,
        x="customer_type",
        y="cancellation_rate",
        text="cancellation_rate"
    )

    fig_cancellation.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig_cancellation.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=80
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Customer Type",
        yaxis_title="Cancellation Rate (%)",
        xaxis_tickangle=-20
    )

    st.plotly_chart(
        fig_cancellation,
        use_container_width=True
    )

    # ========================================================
    # 3. ADR BY CUSTOMER TYPE
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '💵 ADR by Customer Type'
        '</div>',
        unsafe_allow_html=True
    )

    adr_chart = customer_summary.sort_values(
        "average_adr",
        ascending=False
    )

    fig_adr = px.bar(
        adr_chart,
        x="customer_type",
        y="average_adr",
        text="average_adr"
    )

    fig_adr.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_adr.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=80
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Customer Type",
        yaxis_title="Average ADR",
        xaxis_tickangle=-20
    )

    st.plotly_chart(
        fig_adr,
        use_container_width=True
    )

    # ========================================================
    # 4. STAY DURATION BY CUSTOMER TYPE
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '🛏 Stay Duration by Customer Type'
        '</div>',
        unsafe_allow_html=True
    )

    stay_chart = customer_summary.sort_values(
        "average_stay",
        ascending=False
    )

    fig_stay = px.bar(
        stay_chart,
        x="customer_type",
        y="average_stay",
        text="average_stay"
    )

    fig_stay.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside"
    )

    fig_stay.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=80
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Customer Type",
        yaxis_title="Average Stay (Nights)",
        xaxis_tickangle=-20
    )

    st.plotly_chart(
        fig_stay,
        use_container_width=True
    )

    # ========================================================
    # CUSTOMER PERFORMANCE TABLE
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '📋 Customer Type Performance Summary'
        '</div>',
        unsafe_allow_html=True
    )

    display_table = customer_summary.copy()

    display_table = display_table[
        [
            "customer_type",
            "bookings",
            "booking_share",
            "cancellation_rate",
            "average_adr",
            "average_stay",
            "estimated_revenue"
        ]
    ]

    display_table.columns = [
        "Customer Type",
        "Bookings",
        "Booking Share %",
        "Cancellation Rate %",
        "Average ADR",
        "Average Stay",
        "Estimated Revenue"
    ]

    display_table["Booking Share %"] = (
        display_table["Booking Share %"]
        .round(2)
    )

    display_table["Cancellation Rate %"] = (
        display_table["Cancellation Rate %"]
        .round(2)
    )

    display_table["Average ADR"] = (
        display_table["Average ADR"]
        .round(2)
    )

    display_table["Average Stay"] = (
        display_table["Average Stay"]
        .round(2)
    )

    display_table["Estimated Revenue"] = (
        display_table["Estimated Revenue"]
        .round(2)
    )

    st.dataframe(
        display_table,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # 🔎 CUSTOMER INSIGHTS
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '🔎 Customer Insights'
        '</div>',
        unsafe_allow_html=True
    )

    highest_stay_row = customer_summary.loc[
        customer_summary["average_stay"].idxmax()
    ]

    highest_stay_type = (
        highest_stay_row["customer_type"]
    )

    highest_stay = (
        highest_stay_row["average_stay"]
    )

    highest_revenue_row = customer_summary.loc[
        customer_summary["estimated_revenue"].idxmax()
    ]

    highest_revenue_type = (
        highest_revenue_row["customer_type"]
    )

    highest_revenue = (
        highest_revenue_row["estimated_revenue"]
    )

    insights = [

        (
            "👥 Customer Volume",
            f"{most_common_type} is the dominant customer "
            f"type, generating {most_common_bookings:,} bookings."
        ),

        (
            "❌ Cancellation Risk",
            f"{highest_cancel_type} has the highest "
            f"cancellation rate at "
            f"{highest_cancel_rate:.1f}%."
        ),

        (
            "💵 Pricing Behaviour",
            f"{highest_adr_type} has the highest average "
            f"ADR at {highest_adr:.2f}."
        ),

        (
            "🛏 Stay Behaviour",
            f"{highest_stay_type} has the longest average "
            f"stay at {highest_stay:.1f} nights."
        ),

        (
            "💰 Revenue Contribution",
            f"{highest_revenue_type} generates the highest "
            f"estimated revenue of {highest_revenue:,.0f}."
        )
    ]

    for title, description in insights:

        st.markdown(f"""
        <div class="revenue-insight">

            <div class="revenue-insight-title">
                {title}
            </div>

            <div class="revenue-insight-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # 💡 RECOMMENDATIONS
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '💡 Customer Strategy Recommendations'
        '</div>',
        unsafe_allow_html=True
    )

    recommendations = [

        (
            "Focus on the dominant customer segment",
            f"{most_common_type} represents the largest "
            "customer group. Maintain strong availability "
            "and targeted offers for this segment."
        ),

        (
            "Reduce high-risk cancellations",
            f"Review booking policies for {highest_cancel_type}, "
            "which has the highest cancellation rate. "
            "Consider deposits, reminders or stricter "
            "cancellation conditions where appropriate."
        ),

        (
            "Develop premium offers",
            f"{highest_adr_type} generates the highest ADR. "
            "Consider premium packages, upgrades and "
            "value-added services for this segment."
        ),

        (
            "Encourage longer stays",
            f"{highest_stay_type} has the longest average stay. "
            "Use this segment's behaviour to design "
            "long-stay packages and targeted promotions."
        )
    ]

    for i, recommendation in enumerate(
        recommendations,
        start=1
    ):

        title, description = recommendation

        st.markdown(f"""
        <div class="revenue-recommendation">

            <div class="revenue-recommendation-title">
                💡 Recommendation {i} — {title}
            </div>

            <div class="revenue-recommendation-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

# ============================================================
# 🔁 REPEAT GUEST ANALYSIS
# ============================================================

def render_repeat_guest_analysis(df):

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    if df is None or df.empty:
        st.warning("⚠️ No data available for repeat guest analysis.")
        return

    data = df.copy()

    # --------------------------------------------------------
    # REQUIRED COLUMN CHECK
    # --------------------------------------------------------

    required_columns = [
        "is_repeated_guest",
        "is_canceled",
        "adr"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing_columns:
        st.error(
            "❌ Required columns are missing: "
            + ", ".join(missing_columns)
        )
        return

    # ========================================================
    # DATA TYPE CLEANING
    # ========================================================

    data["is_repeated_guest"] = pd.to_numeric(
        data["is_repeated_guest"],
        errors="coerce"
    ).fillna(0)

    data["is_canceled"] = pd.to_numeric(
        data["is_canceled"],
        errors="coerce"
    ).fillna(0)

    data["adr"] = pd.to_numeric(
        data["adr"],
        errors="coerce"
    ).fillna(0)

    # --------------------------------------------------------
    # CREATE GUEST CATEGORY
    # --------------------------------------------------------

    data["guest_type"] = data["is_repeated_guest"].apply(
        lambda x: "Repeat Guest"
        if x == 1
        else "New Guest"
    )

    # ========================================================
    # CREATE TOTAL STAY NIGHTS
    # ========================================================

    if (
        "stays_in_weekend_nights" in data.columns
        and
        "stays_in_weekdays_nights" in data.columns
    ):

        data["total_stay_nights"] = (
            pd.to_numeric(
                data["stays_in_weekend_nights"],
                errors="coerce"
            ).fillna(0)
            +
            pd.to_numeric(
                data["stays_in_weekdays_nights"],
                errors="coerce"
            ).fillna(0)
        )

    else:

        data["total_stay_nights"] = 0

    # ========================================================
    # ESTIMATED REVENUE
    # ========================================================

    data["estimated_revenue"] = (
        data["adr"]
        *
        data["total_stay_nights"]
    )

    # ========================================================
    # PAGE HEADER
    # ========================================================

    st.markdown("""
    <div class="revenue-header">

        <div class="revenue-title">
            🔁 Repeat Guest Analysis
        </div>

        <div class="revenue-subtitle">
            Compare new and repeat guests to understand
            loyalty, cancellation behaviour, pricing,
            stay duration and revenue contribution.
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # GUEST SUMMARY
    # ========================================================

    guest_summary = (
        data
        .groupby("guest_type")
        .agg(
            bookings=("guest_type", "size"),
            cancellations=("is_canceled", "sum"),
            average_adr=("adr", "mean"),
            average_stay=("total_stay_nights", "mean"),
            estimated_revenue=("estimated_revenue", "sum")
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # CANCELLATION RATE
    # --------------------------------------------------------

    guest_summary["cancellation_rate"] = (
        guest_summary["cancellations"]
        /
        guest_summary["bookings"]
        *
        100
    )

    # --------------------------------------------------------
    # GUEST SHARE
    # --------------------------------------------------------

    total_bookings = len(data)

    guest_summary["guest_share"] = (
        guest_summary["bookings"]
        /
        total_bookings
        *
        100
    )

    # ========================================================
    # ENSURE BOTH CATEGORIES EXIST
    # ========================================================

    expected_guest_types = [
        "New Guest",
        "Repeat Guest"
    ]

    for guest_type in expected_guest_types:

        if guest_type not in guest_summary["guest_type"].values:

            guest_summary = pd.concat(
                [
                    guest_summary,
                    pd.DataFrame({
                        "guest_type": [guest_type],
                        "bookings": [0],
                        "cancellations": [0],
                        "average_adr": [0],
                        "average_stay": [0],
                        "estimated_revenue": [0],
                        "cancellation_rate": [0],
                        "guest_share": [0]
                    })
                ],
                ignore_index=True
            )

    guest_summary["guest_type"] = pd.Categorical(
        guest_summary["guest_type"],
        categories=expected_guest_types,
        ordered=True
    )

    guest_summary = guest_summary.sort_values(
        "guest_type"
    )

    # ========================================================
    # KPI CALCULATIONS
    # ========================================================

    repeat_guest_row = guest_summary[
        guest_summary["guest_type"] == "Repeat Guest"
    ].iloc[0]

    new_guest_row = guest_summary[
        guest_summary["guest_type"] == "New Guest"
    ].iloc[0]

    repeat_guest_rate = (
        repeat_guest_row["guest_share"]
    )

    repeat_cancellation_rate = (
        repeat_guest_row["cancellation_rate"]
    )

    repeat_average_adr = (
        repeat_guest_row["average_adr"]
    )

    repeat_average_stay = (
        repeat_guest_row["average_stay"]
    )

    # ========================================================
    # KPI CARDS
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                🔁 REPEAT GUEST RATE
            </div>

            <div class="revenue-kpi-value">
                {repeat_guest_rate:.1f}%
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                ❌ REPEAT GUEST CANCELLATION
            </div>

            <div class="revenue-kpi-value">
                {repeat_cancellation_rate:.1f}%
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col3:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                💵 REPEAT GUEST ADR
            </div>

            <div class="revenue-kpi-value">
                {repeat_average_adr:.2f}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col4:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                🛏 REPEAT GUEST AVERAGE STAY
            </div>

            <div class="revenue-kpi-value">
                {repeat_average_stay:.1f} nights
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # 1. NEW VS REPEAT GUESTS
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '👥 New vs Repeat Guests'
        '</div>',
        unsafe_allow_html=True
    )

    fig_guests = px.bar(
        guest_summary,
        x="guest_type",
        y="bookings",
        text="bookings"
    )

    fig_guests.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig_guests.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=60
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Guest Type",
        yaxis_title="Bookings"
    )

    st.plotly_chart(
        fig_guests,
        use_container_width=True
    )

    # ========================================================
    # 2. CANCELLATION RATE COMPARISON
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '❌ Cancellation Rate Comparison'
        '</div>',
        unsafe_allow_html=True
    )

    fig_cancellation = px.bar(
        guest_summary,
        x="guest_type",
        y="cancellation_rate",
        text="cancellation_rate"
    )

    fig_cancellation.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig_cancellation.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=60
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Guest Type",
        yaxis_title="Cancellation Rate (%)"
    )

    st.plotly_chart(
        fig_cancellation,
        use_container_width=True
    )

    # ========================================================
    # 3. ADR COMPARISON
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '💵 ADR Comparison'
        '</div>',
        unsafe_allow_html=True
    )

    fig_adr = px.bar(
        guest_summary,
        x="guest_type",
        y="average_adr",
        text="average_adr"
    )

    fig_adr.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_adr.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=60
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Guest Type",
        yaxis_title="Average ADR"
    )

    st.plotly_chart(
        fig_adr,
        use_container_width=True
    )

    # ========================================================
    # 4. STAY DURATION COMPARISON
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '🛏 Stay Duration Comparison'
        '</div>',
        unsafe_allow_html=True
    )

    fig_stay = px.bar(
        guest_summary,
        x="guest_type",
        y="average_stay",
        text="average_stay"
    )

    fig_stay.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside"
    )

    fig_stay.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=60
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Guest Type",
        yaxis_title="Average Stay (Nights)"
    )

    st.plotly_chart(
        fig_stay,
        use_container_width=True
    )

    # ========================================================
    # 5. REVENUE COMPARISON
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '💰 Estimated Revenue Comparison'
        '</div>',
        unsafe_allow_html=True
    )

    fig_revenue = px.bar(
        guest_summary,
        x="guest_type",
        y="estimated_revenue",
        text="estimated_revenue"
    )

    fig_revenue.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside"
    )

    fig_revenue.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=60
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Guest Type",
        yaxis_title="Estimated Revenue"
    )

    st.plotly_chart(
        fig_revenue,
        use_container_width=True
    )

    # ========================================================
    # PERFORMANCE TABLE
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '📋 New vs Repeat Guest Performance'
        '</div>',
        unsafe_allow_html=True
    )

    display_table = guest_summary.copy()

    display_table = display_table[
        [
            "guest_type",
            "bookings",
            "guest_share",
            "cancellation_rate",
            "average_adr",
            "average_stay",
            "estimated_revenue"
        ]
    ]

    display_table.columns = [
        "Guest Type",
        "Bookings",
        "Guest Share %",
        "Cancellation Rate %",
        "Average ADR",
        "Average Stay",
        "Estimated Revenue"
    ]

    display_table["Guest Share %"] = (
        display_table["Guest Share %"]
        .round(2)
    )

    display_table["Cancellation Rate %"] = (
        display_table["Cancellation Rate %"]
        .round(2)
    )

    display_table["Average ADR"] = (
        display_table["Average ADR"]
        .round(2)
    )

    display_table["Average Stay"] = (
        display_table["Average Stay"]
        .round(2)
    )

    display_table["Estimated Revenue"] = (
        display_table["Estimated Revenue"]
        .round(2)
    )

    st.dataframe(
        display_table,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # 🔎 BUSINESS INSIGHTS
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '🔎 Repeat Guest Insights'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # CANCELLATION COMPARISON
    # --------------------------------------------------------

    cancellation_difference = (
        new_guest_row["cancellation_rate"]
        -
        repeat_guest_row["cancellation_rate"]
    )

    if cancellation_difference > 0:

        cancellation_insight = (
            f"Repeat guests have a lower cancellation rate "
            f"({repeat_cancellation_rate:.1f}%) than new guests "
            f"({new_guest_row['cancellation_rate']:.1f}%), "
            f"a difference of {cancellation_difference:.1f} "
            "percentage points."
        )

    elif cancellation_difference < 0:

        cancellation_insight = (
            f"Repeat guests have a higher cancellation rate "
            f"({repeat_cancellation_rate:.1f}%) than new guests "
            f"({new_guest_row['cancellation_rate']:.1f}%)."
        )

    else:

        cancellation_insight = (
            "Repeat and new guests have the same cancellation rate."
        )

    # --------------------------------------------------------
    # STAY COMPARISON
    # --------------------------------------------------------

    stay_difference = (
        repeat_guest_row["average_stay"]
        -
        new_guest_row["average_stay"]
    )

    if stay_difference > 0:

        stay_insight = (
            f"Repeat guests stay longer on average at "
            f"{repeat_average_stay:.1f} nights compared with "
            f"{new_guest_row['average_stay']:.1f} nights for "
            "new guests."
        )

    elif stay_difference < 0:

        stay_insight = (
            f"New guests stay longer on average at "
            f"{new_guest_row['average_stay']:.1f} nights "
            f"compared with {repeat_average_stay:.1f} nights "
            "for repeat guests."
        )

    else:

        stay_insight = (
            "New and repeat guests have the same average stay duration."
        )

    # --------------------------------------------------------
    # ADR COMPARISON
    # --------------------------------------------------------

    adr_difference = (
        repeat_guest_row["average_adr"]
        -
        new_guest_row["average_adr"]
    )

    if adr_difference > 0:

        adr_insight = (
            f"Repeat guests generate a higher average ADR "
            f"({repeat_average_adr:.2f}) than new guests "
            f"({new_guest_row['average_adr']:.2f})."
        )

    elif adr_difference < 0:

        adr_insight = (
            f"New guests generate a higher average ADR "
            f"({new_guest_row['average_adr']:.2f}) than "
            f"repeat guests ({repeat_average_adr:.2f})."
        )

    else:

        adr_insight = (
            "New and repeat guests have the same average ADR."
        )

    # --------------------------------------------------------
    # REVENUE COMPARISON
    # --------------------------------------------------------

    repeat_revenue = (
        repeat_guest_row["estimated_revenue"]
    )

    new_revenue = (
        new_guest_row["estimated_revenue"]
    )

    if repeat_revenue > new_revenue:

        revenue_insight = (
            f"Repeat guests generate higher estimated revenue "
            f"({repeat_revenue:,.0f}) than new guests "
            f"({new_revenue:,.0f})."
        )

    elif repeat_revenue < new_revenue:

        revenue_insight = (
            f"New guests generate higher estimated revenue "
            f"({new_revenue:,.0f}) than repeat guests "
            f"({repeat_revenue:,.0f})."
        )

    else:

        revenue_insight = (
            "New and repeat guests generate the same estimated revenue."
        )

    insights = [

        (
            "🔁 Guest Loyalty",
            f"Repeat guests represent {repeat_guest_rate:.1f}% "
            "of all bookings."
        ),

        (
            "❌ Cancellation Behaviour",
            cancellation_insight
        ),

        (
            "🛏 Stay Behaviour",
            stay_insight
        ),

        (
            "💵 Pricing Behaviour",
            adr_insight
        ),

        (
            "💰 Revenue Contribution",
            revenue_insight
        )
    ]

    for title, description in insights:

        st.markdown(f"""
        <div class="revenue-insight">

            <div class="revenue-insight-title">
                {title}
            </div>

            <div class="revenue-insight-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # 💡 RECOMMENDATIONS
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '💡 Repeat Guest Recommendations'
        '</div>',
        unsafe_allow_html=True
    )

    recommendations = [

        (
            "Strengthen guest loyalty",
            "Introduce loyalty benefits, returning-guest "
            "discounts and personalized offers to encourage "
            "new customers to become repeat guests."
        ),

        (
            "Target repeat guests directly",
            "Use previous booking behaviour to create "
            "personalized campaigns for repeat guests "
            "and encourage direct bookings."
        ),

        (
            "Reduce cancellation risk",
            "Compare cancellation behaviour between new and "
            "repeat guests and use flexible but controlled "
            "booking policies to reduce avoidable cancellations."
        ),

        (
            "Increase repeat guest value",
            "Consider room upgrades, premium packages and "
            "additional services for loyal customers when "
            "their booking behaviour supports higher-value offers."
        )
    ]

    for i, recommendation in enumerate(
        recommendations,
        start=1
    ):

        title, description = recommendation

        st.markdown(f"""
        <div class="revenue-recommendation">

            <div class="revenue-recommendation-title">
                💡 Recommendation {i} — {title}
            </div>

            <div class="revenue-recommendation-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

# ============================================================
# 🍽️ MEAL PREFERENCE ANALYSIS
# ============================================================

def render_meal_analysis(df):

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    if df is None or df.empty:
        st.warning("⚠️ No data available for meal analysis.")
        return

    data = df.copy()

    # --------------------------------------------------------
    # REQUIRED COLUMN CHECK
    # --------------------------------------------------------

    required_columns = [
        "meal",
        "is_canceled",
        "adr",
        "hotel"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing_columns:
        st.error(
            "❌ Required columns are missing: "
            + ", ".join(missing_columns)
        )
        return

    # --------------------------------------------------------
    # DATA CLEANING
    # --------------------------------------------------------

    data["meal"] = (
        data["meal"]
        .fillna("Undefined")
        .astype(str)
        .str.strip()
    )

    data.loc[
        data["meal"].isin(["", "nan", "None"]),
        "meal"
    ] = "Undefined"

    data["is_canceled"] = pd.to_numeric(
        data["is_canceled"],
        errors="coerce"
    ).fillna(0)

    data["adr"] = pd.to_numeric(
        data["adr"],
        errors="coerce"
    ).fillna(0)

    # ========================================================
    # CREATE TOTAL STAY NIGHTS
    # ========================================================

    if (
        "stays_in_weekend_nights" in data.columns
        and
        "stays_in_weekdays_nights" in data.columns
    ):

        data["total_stay_nights"] = (
            pd.to_numeric(
                data["stays_in_weekend_nights"],
                errors="coerce"
            ).fillna(0)
            +
            pd.to_numeric(
                data["stays_in_weekdays_nights"],
                errors="coerce"
            ).fillna(0)
        )

    else:

        data["total_stay_nights"] = 0

    # --------------------------------------------------------
    # ESTIMATED REVENUE
    # --------------------------------------------------------

    data["estimated_revenue"] = (
        data["adr"]
        *
        data["total_stay_nights"]
    )

    # ========================================================
    # PAGE HEADER
    # ========================================================

    st.markdown("""
    <div class="revenue-header">

        <div class="revenue-title">
            🍽️ Meal Preference Analysis
        </div>

        <div class="revenue-subtitle">
            Analyze meal package preferences and understand
            how meal selections relate to booking volume,
            cancellation behaviour, pricing and hotel type.
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # MEAL SUMMARY
    # ========================================================

    meal_summary = (
        data
        .groupby("meal")
        .agg(
            bookings=("meal", "size"),
            cancellations=("is_canceled", "sum"),
            average_adr=("adr", "mean"),
            estimated_revenue=("estimated_revenue", "sum")
        )
        .reset_index()
    )

    meal_summary["cancellation_rate"] = (
        meal_summary["cancellations"]
        /
        meal_summary["bookings"]
        *
        100
    )

    meal_summary["booking_share"] = (
        meal_summary["bookings"]
        /
        len(data)
        *
        100
    )

    meal_summary = meal_summary.sort_values(
        "bookings",
        ascending=False
    )

    # ========================================================
    # KPI CALCULATIONS
    # ========================================================

    most_popular_row = meal_summary.iloc[0]

    most_popular_meal = (
        most_popular_row["meal"]
    )

    most_popular_share = (
        most_popular_row["booking_share"]
    )

    highest_cancel_row = meal_summary.loc[
        meal_summary["cancellation_rate"].idxmax()
    ]

    highest_cancel_meal = (
        highest_cancel_row["meal"]
    )

    highest_cancel_rate = (
        highest_cancel_row["cancellation_rate"]
    )

    highest_adr_row = meal_summary.loc[
        meal_summary["average_adr"].idxmax()
    ]

    highest_adr_meal = (
        highest_adr_row["meal"]
    )

    highest_adr = (
        highest_adr_row["average_adr"]
    )

    # ========================================================
    # KPI CARDS
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                🍽️ MOST POPULAR MEAL
            </div>

            <div class="revenue-kpi-value">
                {most_popular_meal}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                📊 TOP MEAL SHARE
            </div>

            <div class="revenue-kpi-value">
                {most_popular_share:.1f}%
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col3:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                ❌ HIGHEST CANCELLATION
            </div>

            <div class="revenue-kpi-value">
                {highest_cancel_rate:.1f}%
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col4:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                💵 HIGHEST MEAL ADR
            </div>

            <div class="revenue-kpi-value">
                {highest_adr:.2f}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # 1. BOOKINGS BY MEAL
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '📊 Bookings by Meal'
        '</div>',
        unsafe_allow_html=True
    )

    fig_bookings = px.bar(
        meal_summary,
        x="meal",
        y="bookings",
        text="bookings"
    )

    fig_bookings.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig_bookings.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=60
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Meal Type",
        yaxis_title="Bookings"
    )

    st.plotly_chart(
        fig_bookings,
        use_container_width=True
    )

    # ========================================================
    # 2. CANCELLATION RATE BY MEAL
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '❌ Cancellation Rate by Meal'
        '</div>',
        unsafe_allow_html=True
    )

    cancellation_chart = meal_summary.sort_values(
        "cancellation_rate",
        ascending=False
    )

    fig_cancellation = px.bar(
        cancellation_chart,
        x="meal",
        y="cancellation_rate",
        text="cancellation_rate"
    )

    fig_cancellation.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig_cancellation.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=60
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Meal Type",
        yaxis_title="Cancellation Rate (%)"
    )

    st.plotly_chart(
        fig_cancellation,
        use_container_width=True
    )

    # ========================================================
    # 3. ADR BY MEAL
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '💵 ADR by Meal'
        '</div>',
        unsafe_allow_html=True
    )

    adr_chart = meal_summary.sort_values(
        "average_adr",
        ascending=False
    )

    fig_adr = px.bar(
        adr_chart,
        x="meal",
        y="average_adr",
        text="average_adr"
    )

    fig_adr.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_adr.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=60
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Meal Type",
        yaxis_title="Average ADR"
    )

    st.plotly_chart(
        fig_adr,
        use_container_width=True
    )

    # ========================================================
    # 4. HOTEL TYPE × MEAL
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '🏨 Hotel Type × Meal Preference'
        '</div>',
        unsafe_allow_html=True
    )

    hotel_meal = (
        data
        .groupby(["hotel", "meal"])
        .size()
        .reset_index(name="bookings")
    )

    fig_hotel_meal = px.bar(
        hotel_meal,
        x="meal",
        y="bookings",
        color="hotel",
        barmode="group",
        text="bookings"
    )

    fig_hotel_meal.update_traces(
        textposition="outside"
    )

    fig_hotel_meal.update_layout(
        height=500,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=60
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Meal Type",
        yaxis_title="Bookings"
    )

    st.plotly_chart(
        fig_hotel_meal,
        use_container_width=True
    )

    # ========================================================
    # PERFORMANCE TABLE
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '📋 Meal Performance Summary'
        '</div>',
        unsafe_allow_html=True
    )

    display_table = meal_summary[
        [
            "meal",
            "bookings",
            "booking_share",
            "cancellation_rate",
            "average_adr",
            "estimated_revenue"
        ]
    ].copy()

    display_table.columns = [
        "Meal",
        "Bookings",
        "Booking Share %",
        "Cancellation Rate %",
        "Average ADR",
        "Estimated Revenue"
    ]

    display_table["Booking Share %"] = (
        display_table["Booking Share %"].round(2)
    )

    display_table["Cancellation Rate %"] = (
        display_table["Cancellation Rate %"].round(2)
    )

    display_table["Average ADR"] = (
        display_table["Average ADR"].round(2)
    )

    display_table["Estimated Revenue"] = (
        display_table["Estimated Revenue"].round(2)
    )

    st.dataframe(
        display_table,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # 🔎 INSIGHTS
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '🔎 Meal Preference Insights'
        '</div>',
        unsafe_allow_html=True
    )

    insights = [

        (
            "🍽️ Customer Preference",
            f"{most_popular_meal} is the most popular meal "
            f"option, accounting for {most_popular_share:.1f}% "
            "of bookings."
        ),

        (
            "❌ Cancellation Behaviour",
            f"{highest_cancel_meal} has the highest "
            f"cancellation rate at {highest_cancel_rate:.1f}%."
        ),

        (
            "💵 Pricing Behaviour",
            f"{highest_adr_meal} has the highest average ADR "
            f"at {highest_adr:.2f}."
        )
    ]

    for title, description in insights:

        st.markdown(f"""
        <div class="revenue-insight">

            <div class="revenue-insight-title">
                {title}
            </div>

            <div class="revenue-insight-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # 💡 RECOMMENDATIONS
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '💡 Meal Strategy Recommendations'
        '</div>',
        unsafe_allow_html=True
    )

    recommendations = [

        (
            "Optimize popular meal packages",
            f"{most_popular_meal} is the most frequently "
            "selected option. Ensure sufficient capacity "
            "and availability for this package."
        ),

        (
            "Review high-risk meal bookings",
            f"Investigate the cancellation behaviour of "
            f"{highest_cancel_meal} bookings and consider "
            "appropriate booking policies."
        ),

        (
            "Promote higher-value packages",
            f"{highest_adr_meal} has the highest ADR. "
            "Consider bundling this meal option with "
            "premium services or room upgrades."
        )
    ]

    for i, recommendation in enumerate(
        recommendations,
        start=1
    ):

        title, description = recommendation

        st.markdown(f"""
        <div class="revenue-recommendation">

            <div class="revenue-recommendation-title">
                💡 Recommendation {i} — {title}
            </div>

            <div class="revenue-recommendation-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

# ============================================================
# 🚗 SPECIAL REQUIREMENTS ANALYSIS
# ============================================================

def render_special_requirements_analysis(df):

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    if df is None or df.empty:
        st.warning(
            "⚠️ No data available for special requirements analysis."
        )
        return

    data = df.copy()

    # --------------------------------------------------------
    # REQUIRED COLUMN CHECK
    # --------------------------------------------------------

    required_columns = [
        "required_car_parking_spaces",
        "total_of_special_requests",
        "is_canceled",
        "adr"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing_columns:
        st.error(
            "❌ Required columns are missing: "
            + ", ".join(missing_columns)
        )
        return

    # ========================================================
    # DATA TYPE CLEANING
    # ========================================================

    data["required_car_parking_spaces"] = pd.to_numeric(
        data["required_car_parking_spaces"],
        errors="coerce"
    ).fillna(0)

    data["total_of_special_requests"] = pd.to_numeric(
        data["total_of_special_requests"],
        errors="coerce"
    ).fillna(0)

    data["is_canceled"] = pd.to_numeric(
        data["is_canceled"],
        errors="coerce"
    ).fillna(0)

    data["adr"] = pd.to_numeric(
        data["adr"],
        errors="coerce"
    ).fillna(0)

    # ========================================================
    # CREATE TOTAL STAY NIGHTS
    # ========================================================

    if (
        "stays_in_weekend_nights" in data.columns
        and
        "stays_in_weekdays_nights" in data.columns
    ):

        data["total_stay_nights"] = (
            pd.to_numeric(
                data["stays_in_weekend_nights"],
                errors="coerce"
            ).fillna(0)
            +
            pd.to_numeric(
                data["stays_in_weekdays_nights"],
                errors="coerce"
            ).fillna(0)
        )

    else:

        data["total_stay_nights"] = 0

    # --------------------------------------------------------
    # ESTIMATED REVENUE
    # --------------------------------------------------------

    data["estimated_revenue"] = (
        data["adr"]
        *
        data["total_stay_nights"]
    )

    # ========================================================
    # CREATE PARKING CATEGORY
    # ========================================================

    data["parking_requirement"] = data[
        "required_car_parking_spaces"
    ].apply(
        lambda x: "Parking Required"
        if x > 0
        else "No Parking Required"
    )

    # ========================================================
    # CREATE SPECIAL REQUEST GROUP
    # ========================================================

    def classify_requests(value):

        if value == 0:
            return "0 Requests"

        elif value == 1:
            return "1 Request"

        elif value == 2:
            return "2 Requests"

        elif value == 3:
            return "3 Requests"

        else:
            return "4+ Requests"

    data["special_request_group"] = (
        data["total_of_special_requests"]
        .apply(classify_requests)
    )

    # ========================================================
    # PAGE HEADER
    # ========================================================

    st.markdown("""
    <div class="revenue-header">

        <div class="revenue-title">
            🚗 Special Requirements Analysis
        </div>

        <div class="revenue-subtitle">
            Analyze parking requirements and special guest
            requests to understand customer needs,
            cancellation behaviour and pricing patterns.
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # KPI CALCULATIONS
    # ========================================================

    parking_request_rate = (
        (
            data["required_car_parking_spaces"] > 0
        ).mean()
        * 100
    )

    average_special_requests = (
        data["total_of_special_requests"].mean()
    )

    maximum_special_requests = (
        data["total_of_special_requests"].max()
    )

    cancellation_rate = (
        data["is_canceled"].mean()
        * 100
    )

    # ========================================================
    # KPI CARDS
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                🚗 PARKING REQUEST RATE
            </div>

            <div class="revenue-kpi-value">
                {parking_request_rate:.1f}%
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                📝 AVG SPECIAL REQUESTS
            </div>

            <div class="revenue-kpi-value">
                {average_special_requests:.2f}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col3:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                📌 MAX SPECIAL REQUESTS
            </div>

            <div class="revenue-kpi-value">
                {int(maximum_special_requests)}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col4:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                ❌ OVERALL CANCELLATION
            </div>

            <div class="revenue-kpi-value">
                {cancellation_rate:.1f}%
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # 1. PARKING REQUIREMENT DISTRIBUTION
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '🚗 Parking Requirement Distribution'
        '</div>',
        unsafe_allow_html=True
    )

    parking_summary = (
        data["parking_requirement"]
        .value_counts()
        .reset_index()
    )

    parking_summary.columns = [
        "parking_requirement",
        "bookings"
    ]

    fig_parking = px.bar(
        parking_summary,
        x="parking_requirement",
        y="bookings",
        text="bookings"
    )

    fig_parking.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig_parking.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=60
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Parking Requirement",
        yaxis_title="Bookings"
    )

    st.plotly_chart(
        fig_parking,
        use_container_width=True
    )

    # ========================================================
    # 2. SPECIAL REQUEST DISTRIBUTION
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '📝 Special Requests Distribution'
        '</div>',
        unsafe_allow_html=True
    )

    request_order = [
        "0 Requests",
        "1 Request",
        "2 Requests",
        "3 Requests",
        "4+ Requests"
    ]

    request_summary = (
        data["special_request_group"]
        .value_counts()
        .reindex(request_order, fill_value=0)
        .reset_index()
    )

    request_summary.columns = [
        "request_group",
        "bookings"
    ]

    fig_requests = px.bar(
        request_summary,
        x="request_group",
        y="bookings",
        text="bookings"
    )

    fig_requests.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig_requests.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=60
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Special Request Group",
        yaxis_title="Bookings"
    )

    st.plotly_chart(
        fig_requests,
        use_container_width=True
    )

    # ========================================================
    # 3. SPECIAL REQUESTS VS CANCELLATION
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '❌ Special Requests vs Cancellation'
        '</div>',
        unsafe_allow_html=True
    )

    request_cancellation = (
        data
        .groupby("special_request_group")
        .agg(
            bookings=("special_request_group", "size"),
            cancellations=("is_canceled", "sum")
        )
        .reset_index()
    )

    request_cancellation["cancellation_rate"] = (
        request_cancellation["cancellations"]
        /
        request_cancellation["bookings"]
        *
        100
    )

    request_cancellation["special_request_group"] = pd.Categorical(
        request_cancellation["special_request_group"],
        categories=request_order,
        ordered=True
    )

    request_cancellation = (
        request_cancellation
        .sort_values("special_request_group")
    )

    fig_request_cancel = px.bar(
        request_cancellation,
        x="special_request_group",
        y="cancellation_rate",
        text="cancellation_rate"
    )

    fig_request_cancel.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig_request_cancel.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=60
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Special Request Group",
        yaxis_title="Cancellation Rate (%)"
    )

    st.plotly_chart(
        fig_request_cancel,
        use_container_width=True
    )

    # ========================================================
    # 4. SPECIAL REQUESTS VS ADR
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '💵 Special Requests vs ADR'
        '</div>',
        unsafe_allow_html=True
    )

    request_adr = (
        data
        .groupby("special_request_group")
        .agg(
            average_adr=("adr", "mean")
        )
        .reset_index()
    )

    request_adr["special_request_group"] = pd.Categorical(
        request_adr["special_request_group"],
        categories=request_order,
        ordered=True
    )

    request_adr = request_adr.sort_values(
        "special_request_group"
    )

    fig_request_adr = px.bar(
        request_adr,
        x="special_request_group",
        y="average_adr",
        text="average_adr"
    )

    fig_request_adr.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_request_adr.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=60
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Special Request Group",
        yaxis_title="Average ADR"
    )

    st.plotly_chart(
        fig_request_adr,
        use_container_width=True
    )

    # ========================================================
    # PERFORMANCE TABLE
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '📋 Special Requirements Summary'
        '</div>',
        unsafe_allow_html=True
    )

    requirements_summary = (
        data
        .groupby("special_request_group")
        .agg(
            bookings=("special_request_group", "size"),
            average_requests=(
                "total_of_special_requests",
                "mean"
            ),
            cancellation_rate=(
                "is_canceled",
                "mean"
            ),
            average_adr=("adr", "mean")
        )
        .reset_index()
    )

    requirements_summary["cancellation_rate"] *= 100

    requirements_summary["special_request_group"] = pd.Categorical(
        requirements_summary["special_request_group"],
        categories=request_order,
        ordered=True
    )

    requirements_summary = requirements_summary.sort_values(
        "special_request_group"
    )

    requirements_summary.columns = [
        "Request Group",
        "Bookings",
        "Average Requests",
        "Cancellation Rate %",
        "Average ADR"
    ]

    requirements_summary["Average Requests"] = (
        requirements_summary["Average Requests"].round(2)
    )

    requirements_summary["Cancellation Rate %"] = (
        requirements_summary["Cancellation Rate %"].round(2)
    )

    requirements_summary["Average ADR"] = (
        requirements_summary["Average ADR"].round(2)
    )

    st.dataframe(
        requirements_summary,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # 🔎 INSIGHTS
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '🔎 Special Requirements Insights'
        '</div>',
        unsafe_allow_html=True
    )

    highest_request_group = (
        request_cancellation
        .loc[
            request_cancellation["bookings"].idxmax(),
            "special_request_group"
        ]
    )

    highest_request_cancel = (
        request_cancellation
        .loc[
            request_cancellation["cancellation_rate"].idxmax(),
            "special_request_group"
        ]
    )

    highest_request_cancel_rate = (
        request_cancellation[
            request_cancellation["special_request_group"]
            ==
            highest_request_cancel
        ]["cancellation_rate"].iloc[0]
    )

    highest_request_adr = (
        request_adr
        .loc[
            request_adr["average_adr"].idxmax(),
            "special_request_group"
        ]
    )

    insights = [

        (
            "🚗 Parking Demand",
            f"{parking_request_rate:.1f}% of bookings "
            "request at least one parking space."
        ),

        (
            "📝 Request Behaviour",
            f"{highest_request_group} is the most common "
            "special-request category."
        ),

        (
            "❌ Cancellation Behaviour",
            f"{highest_request_cancel} has the highest "
            f"cancellation rate at "
            f"{highest_request_cancel_rate:.1f}%."
        ),

        (
            "💵 Pricing Behaviour",
            f"{highest_request_adr} has the highest average "
            "ADR among the request groups."
        )
    ]

    for title, description in insights:

        st.markdown(f"""
        <div class="revenue-insight">

            <div class="revenue-insight-title">
                {title}
            </div>

            <div class="revenue-insight-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # 💡 RECOMMENDATIONS
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '💡 Special Requirements Recommendations'
        '</div>',
        unsafe_allow_html=True
    )

    recommendations = [

        (
            "Plan parking capacity",
            f"{parking_request_rate:.1f}% of bookings "
            "request parking. Hotels should monitor parking "
            "capacity during periods of high demand."
        ),

        (
            "Prioritize common requests",
            f"{highest_request_group} represents the most "
            "common request level. Staff and operational "
            "resources should be prepared for this demand."
        ),

        (
            "Investigate high-risk groups",
            f"{highest_request_cancel} has the highest "
            "cancellation rate. Review the booking behaviour "
            "of this group to identify potential cancellation drivers."
        ),

        (
            "Use requests for personalization",
            "Special requests can provide useful signals "
            "about guest needs. Hotels can use this information "
            "to improve personalization and guest experience."
        )
    ]

    for i, recommendation in enumerate(
        recommendations,
        start=1
    ):

        title, description = recommendation

        st.markdown(f"""
        <div class="revenue-recommendation">

            <div class="revenue-recommendation-title">
                💡 Recommendation {i} — {title}
            </div>

            <div class="revenue-recommendation-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

# ============================================================
# 👨‍👩‍👧 GUEST COMPOSITION ANALYSIS
# ============================================================

def render_guest_composition_analysis(df):

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    if df is None or df.empty:
        st.warning("⚠️ No data available for guest composition analysis.")
        return

    data = df.copy()

    # --------------------------------------------------------
    # REQUIRED COLUMNS
    # --------------------------------------------------------

    required_columns = [
        "adults",
        "children",
        "babies",
        "adr",
        "is_canceled"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing_columns:
        st.error(
            "❌ Required columns are missing: "
            + ", ".join(missing_columns)
        )
        return

    # --------------------------------------------------------
    # DATA TYPES
    # --------------------------------------------------------

    for col in [
        "adults",
        "children",
        "babies",
        "adr",
        "is_canceled"
    ]:
        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        ).fillna(0)

    # --------------------------------------------------------
    # TOTAL GUESTS
    # --------------------------------------------------------

    data["total_guests"] = (
        data["adults"]
        + data["children"]
        + data["babies"]
    )

    # --------------------------------------------------------
    # FAMILY BOOKING
    # Family = at least one child or baby
    # --------------------------------------------------------

    data["family_booking"] = (
        (data["children"] > 0)
        |
        (data["babies"] > 0)
    )

    # --------------------------------------------------------
    # TOTAL STAY
    # --------------------------------------------------------

    if (
        "stays_in_weekend_nights" in data.columns
        and
        "stays_in_weekdays_nights" in data.columns
    ):

        data["total_stay_nights"] = (
            pd.to_numeric(
                data["stays_in_weekend_nights"],
                errors="coerce"
            ).fillna(0)
            +
            pd.to_numeric(
                data["stays_in_weekdays_nights"],
                errors="coerce"
            ).fillna(0)
        )

    else:
        data["total_stay_nights"] = 0

    # ========================================================
    # PAGE HEADER
    # ========================================================

    st.markdown("""
    <div class="revenue-header">

        <div class="revenue-title">
            👨‍👩‍👧 Guest Composition Analysis
        </div>

        <div class="revenue-subtitle">
            Understand the composition of hotel bookings by
            adults, children and babies, and identify how
            guest size influences pricing, cancellations
            and length of stay.
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # KPI CALCULATIONS
    # ========================================================

    avg_guests = data["total_guests"].mean()

    avg_adults = data["adults"].mean()

    avg_children = data["children"].mean()

    family_booking_rate = (
        data["family_booking"].mean()
        * 100
    )

    # ========================================================
    # KPI CARDS
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                👥 AVG GUESTS / BOOKING
            </div>

            <div class="revenue-kpi-value">
                {avg_guests:.2f}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                👨 AVG ADULTS
            </div>

            <div class="revenue-kpi-value">
                {avg_adults:.2f}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col3:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                👧 AVG CHILDREN
            </div>

            <div class="revenue-kpi-value">
                {avg_children:.2f}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col4:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                👨‍👩‍👧 FAMILY BOOKINGS
            </div>

            <div class="revenue-kpi-value">
                {family_booking_rate:.1f}%
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # 1. GUEST COMPOSITION
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '👨‍👩‍👧 Guest Composition'
        '</div>',
        unsafe_allow_html=True
    )

    composition = pd.DataFrame({
        "Guest Type": [
            "Adults",
            "Children",
            "Babies"
        ],
        "Guests": [
            data["adults"].sum(),
            data["children"].sum(),
            data["babies"].sum()
        ]
    })

    fig_composition = px.bar(
        composition,
        x="Guest Type",
        y="Guests",
        text="Guests"
    )

    fig_composition.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig_composition.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=60
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Guest Type",
        yaxis_title="Number of Guests"
    )

    st.plotly_chart(
        fig_composition,
        use_container_width=True
    )

    # ========================================================
    # 2. TOTAL GUESTS DISTRIBUTION
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '📊 Total Guests Distribution'
        '</div>',
        unsafe_allow_html=True
    )

    guest_distribution = (
        data["total_guests"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    guest_distribution.columns = [
        "total_guests",
        "bookings"
    ]

    fig_distribution = px.bar(
        guest_distribution,
        x="total_guests",
        y="bookings",
        text="bookings"
    )

    fig_distribution.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig_distribution.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=60
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Total Guests",
        yaxis_title="Bookings"
    )

    st.plotly_chart(
        fig_distribution,
        use_container_width=True
    )

    # ========================================================
    # 3. GUESTS VS ADR
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '💵 Guests vs ADR'
        '</div>',
        unsafe_allow_html=True
    )

    guests_adr = (
        data
        .groupby("total_guests")
        .agg(
            average_adr=("adr", "mean"),
            bookings=("total_guests", "size")
        )
        .reset_index()
    )

    fig_guests_adr = px.bar(
        guests_adr,
        x="total_guests",
        y="average_adr",
        text="average_adr"
    )

    fig_guests_adr.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_guests_adr.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=60
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Total Guests",
        yaxis_title="Average ADR"
    )

    st.plotly_chart(
        fig_guests_adr,
        use_container_width=True
    )

    # ========================================================
    # 4. GUESTS VS CANCELLATION
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '❌ Guests vs Cancellation'
        '</div>',
        unsafe_allow_html=True
    )

    guests_cancel = (
        data
        .groupby("total_guests")
        .agg(
            bookings=("total_guests", "size"),
            cancellations=("is_canceled", "sum")
        )
        .reset_index()
    )

    guests_cancel["cancellation_rate"] = (
        guests_cancel["cancellations"]
        /
        guests_cancel["bookings"]
        *
        100
    )

    fig_guests_cancel = px.bar(
        guests_cancel,
        x="total_guests",
        y="cancellation_rate",
        text="cancellation_rate"
    )

    fig_guests_cancel.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig_guests_cancel.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=60
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Total Guests",
        yaxis_title="Cancellation Rate (%)"
    )

    st.plotly_chart(
        fig_guests_cancel,
        use_container_width=True
    )

    # ========================================================
    # 5. GUESTS VS STAY DURATION
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '🛏️ Guests vs Stay Duration'
        '</div>',
        unsafe_allow_html=True
    )

    guests_stay = (
        data
        .groupby("total_guests")
        .agg(
            average_stay=("total_stay_nights", "mean"),
            bookings=("total_guests", "size")
        )
        .reset_index()
    )

    fig_guests_stay = px.bar(
        guests_stay,
        x="total_guests",
        y="average_stay",
        text="average_stay"
    )

    fig_guests_stay.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside"
    )

    fig_guests_stay.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=60
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Total Guests",
        yaxis_title="Average Stay (Nights)"
    )

    st.plotly_chart(
        fig_guests_stay,
        use_container_width=True
    )

    # ========================================================
    # FAMILY VS NON-FAMILY COMPARISON
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '👨‍👩‍👧 Family vs Non-Family Bookings'
        '</div>',
        unsafe_allow_html=True
    )

    family_summary = (
        data
        .groupby("family_booking")
        .agg(
            bookings=("family_booking", "size"),
            cancellation_rate=("is_canceled", "mean"),
            average_adr=("adr", "mean"),
            average_stay=("total_stay_nights", "mean")
        )
        .reset_index()
    )

    family_summary["cancellation_rate"] *= 100

    family_summary["family_booking"] = (
        family_summary["family_booking"]
        .map({
            True: "Family",
            False: "Non-Family"
        })
    )

    fig_family = px.bar(
        family_summary,
        x="family_booking",
        y="bookings",
        text="bookings"
    )

    fig_family.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig_family.update_layout(
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Booking Type",
        yaxis_title="Bookings"
    )

    st.plotly_chart(
        fig_family,
        use_container_width=True
    )

    # ========================================================
    # INSIGHTS
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '🔎 Guest Composition Insights'
        '</div>',
        unsafe_allow_html=True
    )

    largest_guest_group = (
        guest_distribution.loc[
            guest_distribution["bookings"].idxmax(),
            "total_guests"
        ]
    )

    highest_adr_guest_count = (
        guests_adr.loc[
            guests_adr["average_adr"].idxmax(),
            "total_guests"
        ]
    )

    highest_cancel_guest_count = (
        guests_cancel.loc[
            guests_cancel["cancellation_rate"].idxmax(),
            "total_guests"
        ]
    )

    insights = [

        (
            "👥 Typical Booking Size",
            f"Bookings with {int(largest_guest_group)} "
            "guest(s) represent the most common booking size."
        ),

        (
            "💵 Guest Size & Pricing",
            f"Bookings with {int(highest_adr_guest_count)} "
            "guest(s) have the highest average ADR."
        ),

        (
            "❌ Cancellation Risk",
            f"Bookings with {int(highest_cancel_guest_count)} "
            "guest(s) show the highest cancellation rate."
        ),

        (
            "👨‍👩‍👧 Family Demand",
            f"{family_booking_rate:.1f}% of bookings are classified "
            "as family bookings because they include at least "
            "one child or baby."
        )
    ]

    for title, description in insights:

        st.markdown(f"""
        <div class="revenue-insight">

            <div class="revenue-insight-title">
                {title}
            </div>

            <div class="revenue-insight-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '💡 Guest Composition Recommendations'
        '</div>',
        unsafe_allow_html=True
    )

    recommendations = [

        (
            "Optimize family packages",
            "Use family booking patterns to develop suitable "
            "room packages, amenities and services for guests "
            "travelling with children."
        ),

        (
            "Plan room capacity",
            "Monitor booking size distribution to improve "
            "room allocation and capacity planning."
        ),

        (
            "Personalize pricing",
            "Guest composition can be considered alongside "
            "ADR and demand patterns when designing targeted "
            "offers and packages."
        )
    ]

    for i, recommendation in enumerate(
        recommendations,
        start=1
    ):

        title, description = recommendation

        st.markdown(f"""
        <div class="revenue-recommendation">

            <div class="revenue-recommendation-title">
                💡 Recommendation {i} — {title}
            </div>

            <div class="revenue-recommendation-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

original_df = globals().get("original_df", None)
cleaned_df = globals().get("cleaned_df", None)

if cleaned_df is None and original_df is not None:
    cleaned_df = original_df.copy()

if original_df is not None and cleaned_df is not None:

    st.session_state["quality_original_rows"] = len(original_df)

    st.session_state["quality_original_columns"] = len(original_df.columns)

    st.session_state["quality_original_missing"] = (
        original_df.isnull().sum().sum()
    )

    st.session_state["quality_original_duplicates"] = (
        original_df.duplicated().sum()
    )

    st.session_state["quality_duplicates_removed"] = (
        original_df.duplicated().sum()
    )

    st.session_state["quality_missing_fixed"] = (
        original_df.isnull().sum().sum()
        -
        cleaned_df.isnull().sum().sum()
    )

    st.session_state["quality_invalid_removed"] = (
        len(original_df)
        -
        len(cleaned_df)
        -
        st.session_state["quality_duplicates_removed"]
    )

    st.session_state["quality_final_rows"] = len(cleaned_df)

    st.session_state["quality_final_columns"] = len(cleaned_df.columns)

    st.session_state["quality_final_missing"] = (
        cleaned_df.isnull().sum().sum()
    )

    st.session_state["quality_final_duplicates"] = (
        cleaned_df.duplicated().sum()
    )

# ============================================================
# 🧹 DATA QUALITY / CLEANING ANALYSIS
# ============================================================

def render_data_quality_analysis(df):

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    if df is None or df.empty:
        st.warning("⚠️ No dataset available.")
        return

    # ========================================================
    # CURRENT DATA QUALITY
    # ========================================================

    current_rows = len(df)

    current_columns = len(df.columns)

    current_missing = (
        df.isnull().sum().sum()
    )

    current_duplicates = (
        df.duplicated().sum()
    )

    # ========================================================
    # ORIGINAL DATA VALUES
    # ========================================================

    original_rows = st.session_state.get(
        "quality_original_rows",
        current_rows
    )

    original_columns = st.session_state.get(
        "quality_original_columns",
        current_columns
    )

    original_missing = st.session_state.get(
        "quality_original_missing",
        current_missing
    )

    original_duplicates = st.session_state.get(
        "quality_original_duplicates",
        current_duplicates
    )

    duplicates_removed = st.session_state.get(
        "quality_duplicates_removed",
        max(
            original_duplicates - current_duplicates,
            0
        )
    )

    missing_fixed = st.session_state.get(
        "quality_missing_fixed",
        max(
            original_missing - current_missing,
            0
        )
    )

    invalid_removed = st.session_state.get(
        "quality_invalid_removed",
        0
    )

    # ========================================================
    # HEADER
    # ========================================================

    st.markdown("""
    <div class="revenue-header">

        <div class="revenue-title">
            🧹 Dataset Quality & Cleaning
        </div>

        <div class="revenue-subtitle">
            Review the quality of the dataset before and
            after preparation, including missing values,
            duplicate records, invalid values and final
            dataset structure.
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # BEFORE CLEANING
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '📥 Before Cleaning'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                📄 ORIGINAL ROWS
            </div>

            <div class="revenue-kpi-value">
                {original_rows:,}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                📊 ORIGINAL COLUMNS
            </div>

            <div class="revenue-kpi-value">
                {original_columns:,}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col3:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                ⚠️ MISSING VALUES
            </div>

            <div class="revenue-kpi-value">
                {original_missing:,}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col4:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                🔁 DUPLICATES
            </div>

            <div class="revenue-kpi-value">
                {original_duplicates:,}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # AFTER CLEANING
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '✅ After Cleaning'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                📄 FINAL ROWS
            </div>

            <div class="revenue-kpi-value">
                {current_rows:,}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                📊 FINAL COLUMNS
            </div>

            <div class="revenue-kpi-value">
                {current_columns:,}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col3:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                ⚠️ REMAINING MISSING
            </div>

            <div class="revenue-kpi-value">
                {current_missing:,}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col4:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                🔁 REMAINING DUPLICATES
            </div>

            <div class="revenue-kpi-value">
                {current_duplicates:,}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # CLEANING SUMMARY
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '🧹 Cleaning Summary'
        '</div>',
        unsafe_allow_html=True
    )

    summary_data = pd.DataFrame({
        "Cleaning Metric": [
            "Original Records",
            "Duplicates Removed",
            "Missing Values Fixed",
            "Invalid Values Removed",
            "Final Records"
        ],
        "Records / Values": [
            original_rows,
            duplicates_removed,
            missing_fixed,
            invalid_removed,
            current_rows
        ]
    })

    st.dataframe(
        summary_data,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # DATA QUALITY COMPARISON
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '📊 Data Quality Comparison'
        '</div>',
        unsafe_allow_html=True
    )

    comparison = pd.DataFrame({
        "Metric": [
            "Rows",
            "Missing Values",
            "Duplicate Rows"
        ],
        "Before Cleaning": [
            original_rows,
            original_missing,
            original_duplicates
        ],
        "After Cleaning": [
            current_rows,
            current_missing,
            current_duplicates
        ]
    })

    comparison_long = comparison.melt(
        id_vars="Metric",
        var_name="Stage",
        value_name="Value"
    )

    fig_quality = px.bar(
        comparison_long,
        x="Metric",
        y="Value",
        color="Stage",
        barmode="group",
        text="Value"
    )

    fig_quality.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig_quality.update_layout(
        height=450,
        margin=dict(
            l=20,
            r=30,
            t=20,
            b=60
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Quality Metric",
        yaxis_title="Count"
    )

    st.plotly_chart(
        fig_quality,
        use_container_width=True
    )

    # ========================================================
    # MISSING VALUES BY COLUMN
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '⚠️ Current Missing Values by Column'
        '</div>',
        unsafe_allow_html=True
    )

    missing_by_column = (
        df.isnull()
        .sum()
        .reset_index()
    )

    missing_by_column.columns = [
        "Column",
        "Missing Values"
    ]

    missing_by_column = (
        missing_by_column[
            missing_by_column["Missing Values"] > 0
        ]
        .sort_values(
            "Missing Values",
            ascending=False
        )
    )

    if missing_by_column.empty:

        st.success(
            "✅ No missing values remain in the cleaned dataset."
        )

    else:

        fig_missing = px.bar(
            missing_by_column,
            x="Column",
            y="Missing Values",
            text="Missing Values"
        )

        fig_missing.update_traces(
            texttemplate="%{text:,}",
            textposition="outside"
        )

        fig_missing.update_layout(
            height=450,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis_title="Column",
            yaxis_title="Missing Values"
        )

        st.plotly_chart(
            fig_missing,
            use_container_width=True
        )

    # ========================================================
    # DATA TYPES
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '🔤 Final Data Types'
        '</div>',
        unsafe_allow_html=True
    )

    dtype_df = pd.DataFrame({
        "Column": df.columns,
        "Data Type": [
            str(dtype)
            for dtype in df.dtypes
        ]
    })

    st.dataframe(
        dtype_df,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # DATASET HEALTH SCORE
    # ========================================================

    missing_score = (
        1
        if current_missing == 0
        else max(
            0,
            1 - (
                current_missing
                /
                max(
                    original_missing,
                    1
                )
            )
        )
    )

    duplicate_score = (
        1
        if current_duplicates == 0
        else max(
            0,
            1 - (
                current_duplicates
                /
                max(
                    original_duplicates,
                    1
                )
            )
        )
    )

    health_score = (
        (
            missing_score
            +
            duplicate_score
        )
        /
        2
        *
        100
    )

    # ========================================================
    # HEALTH CARD
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '❤️ Dataset Health'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(f"""
    <div class="revenue-kpi"
         style="text-align:center;">

        <div class="revenue-kpi-label">
            DATASET QUALITY SCORE
        </div>

        <div class="revenue-kpi-value">
            {health_score:.0f}%
        </div>

        <div style="
            margin-top:10px;
            color:#9ca3af;
            font-size:14px;
        ">
            Based on remaining missing values
            and duplicate records.
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # INSIGHTS
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '🔎 Data Quality Insights'
        '</div>',
        unsafe_allow_html=True
    )

    insights = [

        (
            "📄 Record Reduction",
            f"The dataset changed from {original_rows:,} "
            f"records to {current_rows:,} records after "
            "data preparation."
        ),

        (
            "🔁 Duplicate Handling",
            f"{duplicates_removed:,} duplicate records "
            "were identified and removed during preparation."
        ),

        (
            "⚠️ Missing Value Handling",
            f"{missing_fixed:,} missing values were addressed "
            "during the cleaning process."
        ),

        (
            "❤️ Dataset Health",
            f"The current dataset has a calculated quality "
            f"score of {health_score:.0f}% based on remaining "
            "missing values and duplicates."
        )
    ]

    for title, description in insights:

        st.markdown(f"""
        <div class="revenue-insight">

            <div class="revenue-insight-title">
                {title}
            </div>

            <div class="revenue-insight-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '💡 Data Quality Recommendations'
        '</div>',
        unsafe_allow_html=True
    )

    recommendations = [

        (
            "Maintain validation rules",
            "Apply the same validation and cleaning rules "
            "to future hotel booking datasets before analysis."
        ),

        (
            "Monitor missing values",
            "Regularly check important analytical columns "
            "for missing values before generating KPIs."
        ),

        (
            "Validate data types",
            "Ensure numerical, categorical and date-related "
            "columns are correctly typed before analysis."
        )
    ]

    for i, recommendation in enumerate(
        recommendations,
        start=1
    ):

        title, description = recommendation

        st.markdown(f"""
        <div class="revenue-recommendation">

            <div class="revenue-recommendation-title">
                💡 Recommendation {i} — {title}
            </div>

            <div class="revenue-recommendation-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

# ============================================================
# 🔎 CORRELATION / RELATIONSHIP ANALYSIS
# ============================================================

def render_correlation_analysis(df):

    if df is None or df.empty:
        st.warning("⚠️ No data available for correlation analysis.")
        return

    data = df.copy()

    # --------------------------------------------------------
    # CREATE TOTAL STAY NIGHTS
    # --------------------------------------------------------

    if (
        "stays_in_weekend_nights" in data.columns
        and
        "stays_in_weekdays_nights" in data.columns
    ):
        data["total_stay_nights"] = (
            pd.to_numeric(
                data["stays_in_weekend_nights"],
                errors="coerce"
            ).fillna(0)
            +
            pd.to_numeric(
                data["stays_in_weekdays_nights"],
                errors="coerce"
            ).fillna(0)
        )

    # --------------------------------------------------------
    # NUMERICAL VARIABLES
    # --------------------------------------------------------

    correlation_columns = [
        "lead_time",
        "adr",
        "total_stay_nights",
        "adults",
        "children",
        "babies",
        "previous_cancellations",
        "booking_changes",
        "total_of_special_requests",
        "is_canceled"
    ]

    available_columns = [
        col for col in correlation_columns
        if col in data.columns
    ]

    if len(available_columns) < 2:
        st.error(
            "❌ Not enough numerical variables available "
            "for correlation analysis."
        )
        return

    correlation_data = data[available_columns].copy()

    for col in available_columns:
        correlation_data[col] = pd.to_numeric(
            correlation_data[col],
            errors="coerce"
        )

    correlation_data = correlation_data.dropna()

    # ========================================================
    # HEADER
    # ========================================================

    st.markdown("""
    <div class="revenue-header">

        <div class="revenue-title">
            🔎 Correlation & Relationship Analysis
        </div>

        <div class="revenue-subtitle">
            Explore relationships between booking behaviour,
            pricing, stay duration and cancellation patterns.
            Correlation indicates association, not causation.
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # CORRELATION MATRIX
    # ========================================================

    correlation_matrix = correlation_data.corr()

    # Friendly names for display
    display_names = {
        "lead_time": "Lead Time",
        "adr": "ADR",
        "total_stay_nights": "Stay Duration",
        "adults": "Adults",
        "children": "Children",
        "babies": "Babies",
        "previous_cancellations": "Previous Cancellations",
        "booking_changes": "Booking Changes",
        "total_of_special_requests": "Special Requests",
        "is_canceled": "Is Cancelled"
    }

    correlation_matrix = correlation_matrix.rename(
        index=display_names,
        columns=display_names
    )

    # ========================================================
    # HEATMAP
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '🔥 Correlation Heatmap'
        '</div>',
        unsafe_allow_html=True
    )

    fig_heatmap = px.imshow(
        correlation_matrix,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1
    )

    fig_heatmap.update_layout(
        height=650,
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=80
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    st.plotly_chart(
        fig_heatmap,
        use_container_width=True
    )

    # ========================================================
    # KEY RELATIONSHIPS
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '📌 Key Relationships'
        '</div>',
        unsafe_allow_html=True
    )

    relationships = [
        ("lead_time", "is_canceled", "Lead Time ↔ Cancellation"),
        ("adr", "is_canceled", "ADR ↔ Cancellation"),
        ("total_stay_nights", "is_canceled", "Stay Duration ↔ Cancellation"),
        ("total_of_special_requests", "is_canceled", "Special Requests ↔ Cancellation"),
        ("lead_time", "adr", "Lead Time ↔ ADR")
    ]

    relationship_results = []

    for col1, col2, label in relationships:

        if col1 in correlation_data.columns and col2 in correlation_data.columns:

            value = correlation_data[col1].corr(
                correlation_data[col2]
            )

            relationship_results.append({
                "Relationship": label,
                "Correlation": value
            })

    relationship_df = pd.DataFrame(
        relationship_results
    )

    if not relationship_df.empty:

        relationship_df["Strength"] = (
            relationship_df["Correlation"]
            .abs()
            .apply(
                lambda x:
                "Strong" if x >= 0.60
                else "Moderate" if x >= 0.30
                else "Weak"
            )
        )

        relationship_df["Direction"] = (
            relationship_df["Correlation"]
            .apply(
                lambda x:
                "Positive" if x > 0
                else "Negative" if x < 0
                else "None"
            )
        )

        relationship_df["Correlation"] = (
            relationship_df["Correlation"]
            .round(3)
        )

        st.dataframe(
            relationship_df,
            use_container_width=True,
            hide_index=True
        )

    # ========================================================
    # STRONGEST RELATIONSHIP WITH CANCELLATION
    # ========================================================

    if "is_canceled" in correlation_data.columns:

        cancellation_correlations = (
            correlation_data
            .corr()["is_canceled"]
            .drop("is_canceled")
            .abs()
            .sort_values(
                ascending=False
            )
        )

        if not cancellation_correlations.empty:

            strongest_variable = (
                cancellation_correlations.index[0]
            )

            strongest_value = (
                correlation_data[
                    strongest_variable
                ].corr(
                    correlation_data["is_canceled"]
                )
            )

            readable_name = display_names.get(
                strongest_variable,
                strongest_variable
            )

            direction = (
                "positive"
                if strongest_value > 0
                else "negative"
            )

            st.markdown(f"""
            <div class="revenue-insight">

                <div class="revenue-insight-title">
                    🔎 Strongest Cancellation Relationship
                </div>

                <div class="revenue-insight-text">
                    Among the selected numerical variables,
                    <b>{readable_name}</b> has the strongest
                    absolute correlation with cancellation,
                    with a correlation of
                    <b>{strongest_value:.2f}</b>.
                    The relationship is
                    <b>{direction}</b>.
                </div>

            </div>
            """, unsafe_allow_html=True)

    # ========================================================
    # DISCLAIMER
    # ========================================================

    st.info(
        "⚠️ Correlation measures statistical association. "
        "It does not prove that one variable causes another."
    )

# ============================================================
# 📌 BUSINESS INSIGHTS
# ============================================================

def render_business_insights(df):

    if df is None or df.empty:
        st.warning("⚠️ No data available for business insights.")
        return

    data = df.copy()

    # ========================================================
    # PREPARATION
    # ========================================================

    # Total stay
    if (
        "stays_in_weekend_nights" in data.columns
        and
        "stays_in_weekdays_nights" in data.columns
    ):

        data["total_stay_nights"] = (
            pd.to_numeric(
                data["stays_in_weekend_nights"],
                errors="coerce"
            ).fillna(0)
            +
            pd.to_numeric(
                data["stays_in_weekdays_nights"],
                errors="coerce"
            ).fillna(0)
        )

    # Revenue
    if (
        "adr" in data.columns
        and
        "total_stay_nights" in data.columns
    ):

        data["estimated_revenue"] = (
            pd.to_numeric(
                data["adr"],
                errors="coerce"
            ).fillna(0)
            *
            data["total_stay_nights"]
        )

    # ========================================================
    # HEADER
    # ========================================================

    st.markdown("""
    <div class="revenue-header">

        <div class="revenue-title">
            📌 Business Insights
        </div>

        <div class="revenue-subtitle">
            Automatically generated business findings based
            on the current dataset and active analysis filters.
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # BASIC METRICS
    # ========================================================

    total_bookings = len(data)

    cancelled_bookings = (
        data["is_canceled"].sum()
        if "is_canceled" in data.columns
        else 0
    )

    cancellation_rate = (
        cancelled_bookings
        /
        total_bookings
        *
        100
        if total_bookings > 0
        else 0
    )

    avg_adr = (
        data["adr"].mean()
        if "adr" in data.columns
        else 0
    )

    avg_lead_time = (
        data["lead_time"].mean()
        if "lead_time" in data.columns
        else 0
    )

    avg_stay = (
        data["total_stay_nights"].mean()
        if "total_stay_nights" in data.columns
        else 0
    )

    total_revenue = (
        data["estimated_revenue"].sum()
        if "estimated_revenue" in data.columns
        else 0
    )

    revenue_lost = (
        data.loc[
            data["is_canceled"] == 1,
            "estimated_revenue"
        ].sum()
        if (
            "is_canceled" in data.columns
            and
            "estimated_revenue" in data.columns
        )
        else 0
    )

    # ========================================================
    # KPI SUMMARY
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                📄 BOOKINGS
            </div>

            <div class="revenue-kpi-value">
                {total_bookings:,}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                ❌ CANCELLATION RATE
            </div>

            <div class="revenue-kpi-value">
                {cancellation_rate:.1f}%
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col3:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                💰 AVG ADR
            </div>

            <div class="revenue-kpi-value">
                {avg_adr:.2f}
            </div>

        </div>
        """, unsafe_allow_html=True)

    with col4:

        st.markdown(f"""
        <div class="revenue-kpi">

            <div class="revenue-kpi-label">
                💵 EST. REVENUE
            </div>

            <div class="revenue-kpi-value">
                {total_revenue:,.0f}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # INSIGHT 1 — CANCELLATION RISK
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '❌ Cancellation Risk'
        '</div>',
        unsafe_allow_html=True
    )

    cancellation_insight = (
        f"The current dataset has a cancellation rate of "
        f"{cancellation_rate:.1f}% across {total_bookings:,} "
        "bookings."
    )

    if cancellation_rate >= 40:

        cancellation_insight += (
            " This represents a high level of cancellation "
            "exposure and should be closely monitored."
        )

    elif cancellation_rate >= 20:

        cancellation_insight += (
            " This represents a meaningful level of "
            "cancellation exposure."
        )

    else:

        cancellation_insight += (
            " The overall cancellation level is relatively "
            "low compared with the selected booking volume."
        )

    st.markdown(f"""
    <div class="revenue-insight">

        <div class="revenue-insight-title">
            🔴 Cancellation Risk
        </div>

        <div class="revenue-insight-text">
            {cancellation_insight}
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # INSIGHT 2 — HOTEL PERFORMANCE
    # ========================================================

    if "hotel" in data.columns:

        hotel_summary = (
            data
            .groupby("hotel")
            .agg(
                bookings=("hotel", "size"),
                cancellation_rate=("is_canceled", "mean")
                if "is_canceled" in data.columns
                else ("hotel", "size"),
                adr=("adr", "mean")
                if "adr" in data.columns
                else ("hotel", "size")
            )
            .reset_index()
        )

        hotel_summary["booking_share"] = (
            hotel_summary["bookings"]
            /
            hotel_summary["bookings"].sum()
            *
            100
        )

        dominant_hotel = (
            hotel_summary.loc[
                hotel_summary["bookings"].idxmax(),
                "hotel"
            ]
        )

        dominant_share = (
            hotel_summary.loc[
                hotel_summary["bookings"].idxmax(),
                "booking_share"
            ]
        )

        st.markdown(
            '<div class="revenue-section">'
            '🏨 Hotel Performance'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(f"""
        <div class="revenue-insight">

            <div class="revenue-insight-title">
                🏨 Hotel Booking Volume
            </div>

            <div class="revenue-insight-text">
                <b>{dominant_hotel}</b> accounts for the
                largest share of bookings at approximately
                <b>{dominant_share:.1f}%</b> of the current
                dataset.
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # INSIGHT 3 — SEASONALITY
    # ========================================================

    month_column = None

    if "arrival_date_month" in data.columns:

        month_column = "arrival_date_month"

    if month_column:

        monthly = (
            data[
                month_column
            ]
            .value_counts()
            .reset_index()
        )

        monthly.columns = [
            "month",
            "bookings"
        ]

        peak_month = (
            monthly.loc[
                monthly["bookings"].idxmax(),
                "month"
            ]
        )

        peak_bookings = (
            monthly.loc[
                monthly["bookings"].idxmax(),
                "bookings"
            ]
        )

        low_month = (
            monthly.loc[
                monthly["bookings"].idxmin(),
                "month"
            ]
        )

        st.markdown(
            '<div class="revenue-section">'
            '📅 Seasonality'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(f"""
        <div class="revenue-insight">

            <div class="revenue-insight-title">
                📅 Peak Booking Month
            </div>

            <div class="revenue-insight-text">
                <b>{peak_month}</b> records the highest
                booking volume with approximately
                <b>{peak_bookings:,}</b> bookings.
                The lowest booking volume occurs in
                <b>{low_month}</b>.
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # INSIGHT 4 — REVENUE
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '💰 Revenue Exposure'
        '</div>',
        unsafe_allow_html=True
    )

    revenue_loss_percentage = (
        revenue_lost
        /
        total_revenue
        *
        100
        if total_revenue > 0
        else 0
    )

    st.markdown(f"""
    <div class="revenue-insight">

        <div class="revenue-insight-title">
            💰 Estimated Revenue Exposure
        </div>

        <div class="revenue-insight-text">
            Estimated revenue across the selected bookings is
            <b>{total_revenue:,.2f}</b>, while approximately
            <b>{revenue_lost:,.2f}</b> is associated with
            cancelled bookings.
            This represents approximately
            <b>{revenue_loss_percentage:.1f}%</b>
            of estimated revenue.
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # INSIGHT 5 — CUSTOMER BEHAVIOUR
    # ========================================================

    if "is_repeated_guest" in data.columns:

        repeat_summary = (
            data
            .groupby("is_repeated_guest")
            .agg(
                bookings=("is_repeated_guest", "size"),
                cancellation_rate=("is_canceled", "mean")
                if "is_canceled" in data.columns
                else ("is_repeated_guest", "size"),
                adr=("adr", "mean")
                if "adr" in data.columns
                else ("is_repeated_guest", "size"),
                stay=("total_stay_nights", "mean")
                if "total_stay_nights" in data.columns
                else ("is_repeated_guest", "size")
            )
            .reset_index()
        )

        repeat_summary["guest_type"] = (
            repeat_summary["is_repeated_guest"]
            .map({
                0: "New Guests",
                1: "Repeat Guests"
            })
        )

        st.markdown(
            '<div class="revenue-section">'
            '👥 Customer Behaviour'
            '</div>',
            unsafe_allow_html=True
        )

        if len(repeat_summary) >= 2:

            new_guest = repeat_summary[
                repeat_summary["is_repeated_guest"] == 0
            ]

            repeat_guest = repeat_summary[
                repeat_summary["is_repeated_guest"] == 1
            ]

            if not new_guest.empty and not repeat_guest.empty:

                new_cancel = (
                    new_guest.iloc[0]["cancellation_rate"]
                    * 100
                )

                repeat_cancel = (
                    repeat_guest.iloc[0]["cancellation_rate"]
                    * 100
                )

                if repeat_cancel < new_cancel:

                    behaviour = (
                        "Repeat guests currently show a lower "
                        "cancellation rate than new guests."
                    )

                elif repeat_cancel > new_cancel:

                    behaviour = (
                        "Repeat guests currently show a higher "
                        "cancellation rate than new guests."
                    )

                else:

                    behaviour = (
                        "Repeat and new guests currently show "
                        "similar cancellation rates."
                    )

                st.markdown(f"""
                <div class="revenue-insight">

                    <div class="revenue-insight-title">
                        👥 Repeat Guest Behaviour
                    </div>

                    <div class="revenue-insight-text">
                        {behaviour}
                    </div>

                </div>
                """, unsafe_allow_html=True)

    # ========================================================
    # LEAD TIME INSIGHT
    # ========================================================

    if (
        "lead_time" in data.columns
        and
        "is_canceled" in data.columns
    ):

        median_lead = data["lead_time"].median()

        long_lead = data[
            data["lead_time"] > median_lead
        ]

        short_lead = data[
            data["lead_time"] <= median_lead
        ]

        if not long_lead.empty and not short_lead.empty:

            long_cancel = (
                long_lead["is_canceled"].mean()
                * 100
            )

            short_cancel = (
                short_lead["is_canceled"].mean()
                * 100
            )

            st.markdown(
                '<div class="revenue-section">'
                '⏳ Lead Time Behaviour'
                '</div>',
                unsafe_allow_html=True
            )

            if long_cancel > short_cancel:

                lead_message = (
                    f"Bookings above the median lead time "
                    f"of {median_lead:.0f} days have a higher "
                    f"cancellation rate ({long_cancel:.1f}%) "
                    f"than shorter-lead bookings "
                    f"({short_cancel:.1f}%)."
                )

            else:

                lead_message = (
                    f"Bookings above the median lead time "
                    f"of {median_lead:.0f} days do not show "
                    f"a higher cancellation rate than "
                    "shorter-lead bookings in the current data."
                )

            st.markdown(f"""
            <div class="revenue-insight">

                <div class="revenue-insight-title">
                    ⏳ Lead Time & Cancellation
                </div>

                <div class="revenue-insight-text">
                    {lead_message}
                </div>

            </div>
            """, unsafe_allow_html=True)

    # ========================================================
    # BUSINESS RECOMMENDATIONS
    # ========================================================

    st.markdown(
        '<div class="revenue-section">'
        '💡 Business Recommendations'
        '</div>',
        unsafe_allow_html=True
    )

    recommendations = []

    # Cancellation recommendation
    if cancellation_rate >= 20:

        recommendations.append(
            (
                "Manage cancellation exposure",
                "Consider stronger deposit policies, "
                "pre-arrival reminders and targeted "
                "cancellation-risk monitoring."
            )
        )

    else:

        recommendations.append(
            (
                "Maintain booking stability",
                "Continue monitoring cancellation behaviour "
                "while maintaining flexible booking options "
                "for customers."
            )
        )

    # Seasonality recommendation
    if month_column:

        recommendations.append(
            (
                "Optimize seasonal pricing",
                f"Use demand patterns around the peak month "
                f"({peak_month}) to review pricing, inventory "
                "and promotional strategies."
            )
        )

    # Revenue recommendation
    if revenue_loss_percentage >= 20:

        recommendations.append(
            (
                "Protect revenue",
                "A meaningful portion of estimated revenue "
                "is associated with cancelled bookings. "
                "Prioritize strategies that reduce "
                "high-risk cancellations."
            )
        )

    else:

        recommendations.append(
            (
                "Optimize revenue",
                "Continue monitoring the relationship between "
                "ADR, booking volume and cancellations to "
                "improve revenue performance."
            )
        )

    # Customer recommendation
    if "is_repeated_guest" in data.columns:

        recommendations.append(
            (
                "Strengthen guest retention",
                "Use repeat-guest behaviour to develop "
                "targeted loyalty offers and personalized "
                "booking experiences."
            )
        )

    for i, recommendation in enumerate(
        recommendations[:4],
        start=1
    ):

        title, description = recommendation

        st.markdown(f"""
        <div class="revenue-recommendation">

            <div class="revenue-recommendation-title">
                💡 Recommendation {i} — {title}
            </div>

            <div class="revenue-recommendation-text">
                {description}
            </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # IMPORTANT NOTE
    # ========================================================

    st.info(
        "📌 These insights are generated from the current "
        "dataset. Once your sidebar filters are connected, "
        "the same function will automatically recalculate "
        "the insights using the filtered data."
    )

# ============================================================
# 💡 RECOMMENDATIONS PAGE
# ============================================================

def render_recommendations(df):

    if df is None or df.empty:
        st.warning("⚠️ No data available for recommendations.")
        return

    data = df.copy()

    # --------------------------------------------------------
    # CREATE TOTAL STAY NIGHTS
    # --------------------------------------------------------

    if (
        "stays_in_weekend_nights" in data.columns
        and "stays_in_weekdays_nights" in data.columns
    ):

        data["total_stay_nights"] = (
            pd.to_numeric(
                data["stays_in_weekend_nights"],
                errors="coerce"
            ).fillna(0)
            +
            pd.to_numeric(
                data["stays_in_weekdays_nights"],
                errors="coerce"
            ).fillna(0)
        )

    # --------------------------------------------------------
    # CREATE ESTIMATED REVENUE
    # --------------------------------------------------------

    if (
        "adr" in data.columns
        and "total_stay_nights" in data.columns
    ):

        data["estimated_revenue"] = (
            pd.to_numeric(
                data["adr"],
                errors="coerce"
            ).fillna(0)
            * data["total_stay_nights"]
        )

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.markdown("""
    <div class="revenue-header">

        <div class="revenue-title">
            💡 Business Recommendations
        </div>

        <div class="revenue-subtitle">
            Data-driven recommendations based on booking
            behaviour, cancellation patterns, pricing,
            customer behaviour and demand.
        </div>

    </div>
    """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # BASIC METRICS
    # --------------------------------------------------------

    total_bookings = len(data)

    # Cancellation
    cancellation_rate = 0

    if "is_canceled" in data.columns:

        cancellation_rate = (
            data["is_canceled"].mean() * 100
        )

    # ADR
    avg_adr = 0

    if "adr" in data.columns:

        avg_adr = data["adr"].mean()

    # Lead time
    avg_lead_time = 0

    if "lead_time" in data.columns:

        avg_lead_time = data["lead_time"].mean()

    # Stay
    avg_stay = 0

    if "total_stay_nights" in data.columns:

        avg_stay = data["total_stay_nights"].mean()

    # Revenue
    total_revenue = 0

    if "estimated_revenue" in data.columns:

        total_revenue = data["estimated_revenue"].sum()

    # --------------------------------------------------------
    # RECOMMENDATION LIST
    # --------------------------------------------------------

    recommendations = []

    # ========================================================
    # 1. REDUCE CANCELLATION RISK
    # ========================================================

    if "is_canceled" in data.columns:

        if cancellation_rate >= 30:

            recommendations.append({
                "icon": "🔴",
                "title": "Reduce Cancellation Risk",
                "priority": "High Priority",
                "description": (
                    f"The current cancellation rate is "
                    f"{cancellation_rate:.1f}%, indicating "
                    "significant booking risk."
                ),
                "action": (
                    "Consider stronger deposit policies, "
                    "clear cancellation deadlines and "
                    "automated reminder emails for "
                    "higher-risk bookings."
                )
            })

        elif cancellation_rate >= 15:

            recommendations.append({
                "icon": "🟠",
                "title": "Monitor Cancellation Risk",
                "priority": "Medium Priority",
                "description": (
                    f"The cancellation rate is "
                    f"{cancellation_rate:.1f}%, creating "
                    "a meaningful level of booking uncertainty."
                ),
                "action": (
                    "Use pre-arrival reminders and targeted "
                    "deposit policies for bookings showing "
                    "higher cancellation risk."
                )
            })

        else:

            recommendations.append({
                "icon": "🟢",
                "title": "Maintain Cancellation Stability",
                "priority": "Low Priority",
                "description": (
                    f"The current cancellation rate is "
                    f"{cancellation_rate:.1f}%."
                ),
                "action": (
                    "Maintain the current booking policies "
                    "while continuing to monitor cancellation "
                    "patterns by lead time and channel."
                )
            })

    # ========================================================
    # 2. DYNAMIC PRICING
    # ========================================================

    if "arrival_date_month" in data.columns:

        monthly_bookings = (
            data["arrival_date_month"]
            .value_counts()
        )

        if not monthly_bookings.empty:

            peak_month = monthly_bookings.idxmax()

            peak_volume = monthly_bookings.max()

            average_monthly_volume = (
                monthly_bookings.mean()
            )

            if peak_volume > average_monthly_volume * 1.25:

                recommendations.append({
                    "icon": "📈",
                    "title": "Dynamic Pricing",
                    "priority": "High Priority",
                    "description": (
                        f"{peak_month} currently records the "
                        "highest booking demand."
                    ),
                    "action": (
                        "Consider increasing ADR and protecting "
                        "inventory during high-demand periods, "
                        "while using targeted promotions during "
                        "weaker demand periods."
                    )
                })

            else:

                recommendations.append({
                    "icon": "📊",
                    "title": "Optimize Pricing by Demand",
                    "priority": "Medium Priority",
                    "description": (
                        "Monthly booking volumes do not show "
                        "an extreme concentration of demand."
                    ),
                    "action": (
                        "Use demand-based pricing adjustments "
                        "to balance occupancy and ADR throughout "
                        "the year."
                    )
                })

    # ========================================================
    # 3. EARLY-BIRD STRATEGY
    # ========================================================

    if (
        "lead_time" in data.columns
        and "is_canceled" in data.columns
    ):

        median_lead = data["lead_time"].median()

        early_bookings = data[
            data["lead_time"] > median_lead
        ]

        short_lead_bookings = data[
            data["lead_time"] <= median_lead
        ]

        if (
            not early_bookings.empty
            and not short_lead_bookings.empty
        ):

            early_cancel_rate = (
                early_bookings["is_canceled"].mean()
                * 100
            )

            short_cancel_rate = (
                short_lead_bookings["is_canceled"].mean()
                * 100
            )

            if early_cancel_rate > short_cancel_rate:

                recommendations.append({
                    "icon": "⏳",
                    "title": "Early-Bird Risk Management",
                    "priority": "High Priority",
                    "description": (
                        f"Bookings made further in advance "
                        f"show a higher cancellation rate "
                        f"({early_cancel_rate:.1f}%) compared "
                        f"with shorter-lead bookings "
                        f"({short_cancel_rate:.1f}%)."
                    ),
                    "action": (
                        "Offer early-booking incentives while "
                        "using appropriate deposits or "
                        "cancellation conditions to reduce "
                        "revenue exposure."
                    )
                })

            else:

                recommendations.append({
                    "icon": "⏳",
                    "title": "Strengthen Early-Bird Demand",
                    "priority": "Medium Priority",
                    "description": (
                        "Longer-lead bookings do not currently "
                        "show a higher cancellation rate."
                    ),
                    "action": (
                        "Consider early-bird promotions to "
                        "encourage customers to commit further "
                        "in advance."
                    )
                })

    # ========================================================
    # 4. CUSTOMER RETENTION
    # ========================================================

    if "is_repeated_guest" in data.columns:

        repeat_guests = data[
            data["is_repeated_guest"] == 1
        ]

        repeat_rate = (
            len(repeat_guests)
            /
            total_bookings
            *
            100
            if total_bookings > 0
            else 0
        )

        recommendations.append({
            "icon": "🔁",
            "title": "Customer Retention",
            "priority": "Medium Priority",
            "description": (
                f"Repeat guests currently represent "
                f"{repeat_rate:.1f}% of bookings."
            ),
            "action": (
                "Develop loyalty incentives, personalized "
                "offers and repeat-guest benefits to increase "
                "customer retention."
            )
        })

    # ========================================================
    # 5. CHANNEL OPTIMIZATION
    # ========================================================

    if (
        "distribution_channel" in data.columns
        and "is_canceled" in data.columns
    ):

        channel_summary = (
            data
            .groupby("distribution_channel")
            .agg(
                bookings=("distribution_channel", "size"),
                cancellation_rate=("is_canceled", "mean"),
                adr=("adr", "mean")
                if "adr" in data.columns
                else ("is_canceled", "mean")
            )
            .reset_index()
        )

        if not channel_summary.empty:

            highest_volume_channel = (
                channel_summary.loc[
                    channel_summary["bookings"].idxmax(),
                    "distribution_channel"
                ]
            )

            lowest_cancel_channel = (
                channel_summary.loc[
                    channel_summary["cancellation_rate"].idxmin(),
                    "distribution_channel"
                ]
            )

            recommendations.append({
                "icon": "📢",
                "title": "Channel Optimization",
                "priority": "Medium Priority",
                "description": (
                    f"{highest_volume_channel} generates the "
                    "highest booking volume, while "
                    f"{lowest_cancel_channel} has the lowest "
                    "cancellation rate."
                ),
                "action": (
                    "Prioritize channels that combine strong "
                    "booking volume with lower cancellation "
                    "risk and attractive ADR."
                )
            })

    # ========================================================
    # 6. LOW-SEASON PROMOTIONS
    # ========================================================

    if "arrival_date_month" in data.columns:

        monthly_bookings = (
            data["arrival_date_month"]
            .value_counts()
        )

        if len(monthly_bookings) >= 3:

            low_month = monthly_bookings.idxmin()

            low_volume = monthly_bookings.min()

            average_volume = monthly_bookings.mean()

            if low_volume < average_volume * 0.75:

                recommendations.append({
                    "icon": "📣",
                    "title": "Low-Season Promotions",
                    "priority": "Medium Priority",
                    "description": (
                        f"{low_month} currently has one of "
                        "the weakest booking volumes."
                    ),
                    "action": (
                        "Use targeted discounts, packages or "
                        "value-added offers to stimulate demand "
                        "during weaker periods."
                    )
                })

    # ========================================================
    # 7. LONG-STAY PACKAGES
    # ========================================================

    if (
        "total_stay_nights" in data.columns
        and "is_canceled" in data.columns
    ):

        long_stays = data[
            data["total_stay_nights"] >= 7
        ]

        regular_stays = data[
            data["total_stay_nights"] < 7
        ]

        if (
            not long_stays.empty
            and not regular_stays.empty
        ):

            long_cancel = (
                long_stays["is_canceled"].mean()
                * 100
            )

            regular_cancel = (
                regular_stays["is_canceled"].mean()
                * 100
            )

            if long_cancel <= regular_cancel:

                recommendations.append({
                    "icon": "🛏️",
                    "title": "Long-Stay Packages",
                    "priority": "Medium Priority",
                    "description": (
                        f"Long-stay bookings have a cancellation "
                        f"rate of {long_cancel:.1f}%, compared "
                        f"with {regular_cancel:.1f}% for shorter "
                        "stays."
                    ),
                    "action": (
                        "Consider weekly packages, family "
                        "packages and extended-stay discounts "
                        "to encourage longer bookings."
                    )
                })

    # ========================================================
    # DISPLAY RECOMMENDATIONS
    # ========================================================

    if not recommendations:

        st.info(
            "No recommendations could be generated from "
            "the available data."
        )

        return

    for recommendation in recommendations:

        priority = recommendation["priority"]

        priority_class = (
            "high"
            if "High" in priority
            else "medium"
            if "Medium" in priority
            else "low"
        )

        st.markdown(f"""
        <div class="recommendation-card {priority_class}">

            <div class="recommendation-top">

                <div class="recommendation-icon">
                    {recommendation["icon"]}
                </div>

                <div>

                    <div class="recommendation-title">
                        {recommendation["title"]}
                    </div>

                    <div class="recommendation-priority">
                        {priority}
                    </div>

                </div>

            </div>

            <div class="recommendation-description">
                {recommendation["description"]}
            </div>

            <div class="recommendation-action">

                <b>Recommended Action</b>

                <br>

                {recommendation["action"]}

            </div>

        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<style>

.recommendation-card {
    padding: 24px;
    margin: 16px 0;
    border-radius: 16px;
    background: rgba(20, 20, 20, 0.82);
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow: 0 8px 30px rgba(0,0,0,0.25);
    transition: all 0.3s ease;
}

.recommendation-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 35px rgba(0,255,120,0.15);
}

.recommendation-top {
    display: flex;
    align-items: center;
    gap: 16px;
}

.recommendation-icon {
    font-size: 32px;
}

.recommendation-title {
    font-size: 21px;
    font-weight: 700;
    color: white;
}

.recommendation-priority {
    margin-top: 4px;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.recommendation-description {
    margin-top: 18px;
    color: #d0d0d0;
    font-size: 15px;
    line-height: 1.6;
}

.recommendation-action {
    margin-top: 16px;
    padding: 14px 16px;
    border-radius: 10px;
    background: rgba(255,255,255,0.05);
    color: #eeeeee;
    font-size: 14px;
    line-height: 1.6;
}

.recommendation-action b {
    color: #7dff9b;
}

/* Priority indicators */

.recommendation-card.high {
    border-left: 4px solid #ff4d4d;
}

.recommendation-card.medium {
    border-left: 4px solid #ffc857;
}

.recommendation-card.low {
    border-left: 4px solid #4dff88;
}

.recommendation-card.high .recommendation-priority {
    color: #ff6b6b;
}

.recommendation-card.medium .recommendation-priority {
    color: #ffc857;
}

.recommendation-card.low .recommendation-priority {
    color: #4dff88;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# 🎛️ GLOBAL FILTERS
# ============================================================

def render_global_filters(df):

    if df is None or df.empty:
        return df

    filtered_df = df.copy()

    with st.container():

        st.markdown("""
        <div class="global-filter-header">

            <div class="global-filter-title">
                🎛️ Dashboard Filters
            </div>

            <div class="global-filter-subtitle">
                Filter the entire analysis dashboard
            </div>

        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        # ====================================================
        # HOTEL
        # ====================================================

        with col1:

            if "hotel" in filtered_df.columns:

                hotel_options = sorted(
                    filtered_df["hotel"]
                    .dropna()
                    .unique()
                    .tolist()
                )

                selected_hotel = st.multiselect(
                    "🏨 Hotel",
                    options=hotel_options,
                    default=hotel_options,
                    key="global_hotel"
                )

                if selected_hotel:

                    filtered_df = filtered_df[
                        filtered_df["hotel"]
                        .isin(selected_hotel)
                    ]

        # ====================================================
        # YEAR
        # ====================================================

        with col2:

            if "arrival_date_year" in filtered_df.columns:

                year_options = sorted(
                    pd.to_numeric(
                        filtered_df["arrival_date_year"],
                        errors="coerce"
                    )
                    .dropna()
                    .unique()
                    .tolist()
                )

                selected_year = st.multiselect(
                    "📅 Year",
                    options=year_options,
                    default=year_options,
                    key="global_year"
                )

                if selected_year:

                    filtered_df = filtered_df[
                        pd.to_numeric(
                            filtered_df["arrival_date_year"],
                            errors="coerce"
                        ).isin(selected_year)
                    ]

        # ====================================================
        # MONTH
        # ====================================================

        with col3:

            if "arrival_date_month" in filtered_df.columns:

                month_options = (
                    filtered_df[
                        "arrival_date_month"
                    ]
                    .dropna()
                    .unique()
                    .tolist()
                )

                selected_month = st.multiselect(
                    "📆 Month",
                    options=month_options,
                    default=month_options,
                    key="global_month"
                )

                if selected_month:

                    filtered_df = filtered_df[
                        filtered_df[
                            "arrival_date_month"
                        ].isin(selected_month)
                    ]

        col4, col5, col6 = st.columns(3)

        # ====================================================
        # MARKET SEGMENT
        # ====================================================

        with col4:

            if "market_segment" in filtered_df.columns:

                options = sorted(
                    filtered_df[
                        "market_segment"
                    ]
                    .dropna()
                    .unique()
                    .tolist()
                )

                selected = st.multiselect(
                    "📊 Market Segment",
                    options=options,
                    default=options,
                    key="global_market_segment"
                )

                if selected:

                    filtered_df = filtered_df[
                        filtered_df[
                            "market_segment"
                        ].isin(selected)
                    ]

        # ====================================================
        # DISTRIBUTION CHANNEL
        # ====================================================

        with col5:

            if "distribution_channel" in filtered_df.columns:

                options = sorted(
                    filtered_df[
                        "distribution_channel"
                    ]
                    .dropna()
                    .unique()
                    .tolist()
                )

                selected = st.multiselect(
                    "📢 Distribution Channel",
                    options=options,
                    default=options,
                    key="global_distribution_channel"
                )

                if selected:

                    filtered_df = filtered_df[
                        filtered_df[
                            "distribution_channel"
                        ].isin(selected)
                    ]

        # ====================================================
        # CUSTOMER TYPE
        # ====================================================

        with col6:

            if "customer_type" in filtered_df.columns:

                options = sorted(
                    filtered_df[
                        "customer_type"
                    ]
                    .dropna()
                    .unique()
                    .tolist()
                )

                selected = st.multiselect(
                    "👥 Customer Type",
                    options=options,
                    default=options,
                    key="global_customer_type"
                )

                if selected:

                    filtered_df = filtered_df[
                        filtered_df[
                            "customer_type"
                        ].isin(selected)
                    ]

        col7, col8, col9 = st.columns(3)

        # ====================================================
        # DEPOSIT TYPE
        # ====================================================

        with col7:

            if "deposit_type" in filtered_df.columns:

                options = sorted(
                    filtered_df[
                        "deposit_type"
                    ]
                    .dropna()
                    .unique()
                    .tolist()
                )

                selected = st.multiselect(
                    "💳 Deposit Type",
                    options=options,
                    default=options,
                    key="global_deposit_type"
                )

                if selected:

                    filtered_df = filtered_df[
                        filtered_df[
                            "deposit_type"
                        ].isin(selected)
                    ]

        # ====================================================
        # MEAL
        # ====================================================

        with col8:

            if "meal" in filtered_df.columns:

                options = sorted(
                    filtered_df[
                        "meal"
                    ]
                    .dropna()
                    .unique()
                    .tolist()
                )

                selected = st.multiselect(
                    "🍽️ Meal",
                    options=options,
                    default=options,
                    key="global_meal"
                )

                if selected:

                    filtered_df = filtered_df[
                        filtered_df[
                            "meal"
                        ].isin(selected)
                    ]

        # ====================================================
        # REPEAT GUEST
        # ====================================================

        with col9:

            if "is_repeated_guest" in filtered_df.columns:

                repeat_options = {
                    "New Guests": 0,
                    "Repeat Guests": 1
                }

                selected_repeat = st.multiselect(
                    "🔁 Guest Type",
                    options=list(
                        repeat_options.keys()
                    ),
                    default=list(
                        repeat_options.keys()
                    ),
                    key="global_repeat_guest"
                )

                selected_values = [
                    repeat_options[x]
                    for x in selected_repeat
                ]

                if selected_values:

                    filtered_df = filtered_df[
                        filtered_df[
                            "is_repeated_guest"
                        ].isin(selected_values)
                    ]

        # ====================================================
        # RESET BUTTON
        # ====================================================

        st.markdown("<br>", unsafe_allow_html=True)

        reset_col1, reset_col2, reset_col3 = st.columns(
            [1, 1, 1]
        )

        with reset_col2:

            if st.button(
                "🔄 Reset Filters",
                use_container_width=True,
                key="reset_global_filters"
            ):

                for key in [
                    "global_hotel",
                    "global_year",
                    "global_month",
                    "global_market_segment",
                    "global_distribution_channel",
                    "global_customer_type",
                    "global_deposit_type",
                    "global_meal",
                    "global_repeat_guest"
                ]:

                    if key in st.session_state:
                        del st.session_state[key]

                st.rerun()

    return filtered_df

st.markdown("""
<style>

.global-filter-header {
    padding: 18px 22px;
    margin-bottom: 12px;
    border-radius: 14px;
    background: rgba(20, 20, 20, 0.85);
    border: 1px solid rgba(0,255,120,0.15);
    box-shadow: 0 0 25px rgba(0,255,120,0.08);
}

.global-filter-title {
    color: white;
    font-size: 20px;
    font-weight: 700;
}

.global-filter-subtitle {
    margin-top: 4px;
    color: #9a9a9a;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)