#====================================================================================
# IMPORT LIBRARY
#====================================================================================

import hashlib
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

#====================================================================================
# SIDEBAR SECTION
#====================================================================================


#====================================================================================
# FILTER SECTION
#====================================================================================

def render_filter_box(df):
    st.markdown("""
    <style>
    /* ================================
       FILTER BOX
       ================================ */

    .filter-box {
        background: rgba(20, 20, 20, 0.92);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 22px 24px 20px 24px;
        margin: 15px 0 25px 0;
        box-shadow:
            0 8px 30px rgba(0, 0, 0, 0.35),
            inset 0 0 20px rgba(255, 255, 255, 0.02);
    }

    .filter-title {
        color: white;
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .filter-subtitle {
        color: #a8a8a8;
        font-size: 13px;
        margin-bottom: 18px;
    }

    /* ================================
       FILTER BUTTON
       ================================ */

    .filter-button-container {
        display: flex;
        justify-content: flex-start;
        margin-top: 18px;
    }

    .filter-button-container button {
        background-color: #ff0000 !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 15px !important;
        padding: 10px 28px !important;
        border: 2px solid #ff0000 !important;
        border-radius: 8px !important;
        box-shadow: none !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
    }

    .filter-button-container button:hover {
        background-color: #ff0000 !important;
        color: white !important;
        box-shadow:
            0 0 15px rgba(255, 0, 0, 0.8),
            0 0 30px rgba(255, 0, 0, 0.6),
            0 0 45px rgba(255, 0, 0, 0.35) !important;
        transform: translateY(-1px) !important;
    }

    /* ================================
       RESET BUTTON
       ================================ */

    .reset-button-container {
        display: flex;
        justify-content: flex-start;
        margin-top: 8px;
    }

    .reset-button-container button {
        background-color: transparent !important;
        color: #bbbbbb !important;
        border: 1px solid #555555 !important;
        border-radius: 8px !important;
        font-size: 13px !important;
        transition: all 0.3s ease !important;
    }

    .reset-button-container button:hover {
        color: white !important;
        border-color: #888888 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Filter box
    st.markdown("""
    <div class="filter-box">
        <div class="filter-title">🎛️ Filter Data</div>
        <div class="filter-subtitle">
            Select filters to customize the analysis and visualizations.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ------------------------------------------------
    # FILTER ROW 1
    # ------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        hotel_options = ["All Hotels"] + sorted(
            df["hotel"].dropna().unique().tolist()
        )

        selected_hotel = st.selectbox(
            "🏨 Hotel",
            hotel_options,
            key="filter_hotel"
        )

    with col2:
        year_options = ["All Years"] + sorted(
            df["arrival_date_year"].dropna().unique().tolist()
        )

        selected_year = st.selectbox(
            "📅 Arrival Year",
            year_options,
            key="filter_year"
        )

    with col3:
        month_order = [
            "January", "February", "March", "April",
            "May", "June", "July", "August",
            "September", "October", "November", "December"
        ]

        available_months = [
            month for month in month_order
            if month in df["arrival_date_month"].dropna().unique()
        ]

        month_options = ["All Months"] + available_months

        selected_month = st.selectbox(
            "📆 Arrival Month",
            month_options,
            key="filter_month"
        )

    # ------------------------------------------------
    # FILTER ROW 2
    # ------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        customer_options = ["All Customer Types"] + sorted(
            df["customer_type"].dropna().unique().tolist()
        )

        selected_customer = st.selectbox(
            "👥 Customer Type",
            customer_options,
            key="filter_customer"
        )

    with col2:
        market_options = ["All Market Segments"] + sorted(
            df["market_segment"].dropna().unique().tolist()
        )

        selected_market = st.selectbox(
            "📢 Market Segment",
            market_options,
            key="filter_market"
        )

    with col3:
        channel_options = ["All Channels"] + sorted(
            df["distribution_channel"].dropna().unique().tolist()
        )

        selected_channel = st.selectbox(
            "📡 Distribution Channel",
            channel_options,
            key="filter_channel"
        )

    # ------------------------------------------------
    # FILTER ROW 3
    # ------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        deposit_options = ["All Deposit Types"] + sorted(
            df["deposit_type"].dropna().unique().tolist()
        )

        selected_deposit = st.selectbox(
            "💳 Deposit Type",
            deposit_options,
            key="filter_deposit"
        )

    with col2:
        cancellation_options = [
            "All Bookings",
            "Confirmed Only",
            "Cancelled Only"
        ]

        selected_cancellation = st.selectbox(
            "❌ Cancellation Status",
            cancellation_options,
            key="filter_cancellation"
        )

    with col3:
        repeat_options = [
            "All Guests",
            "New Guests",
            "Repeat Guests"
        ]

        selected_repeat = st.selectbox(
            "🔁 Guest Type",
            repeat_options,
            key="filter_repeat"
        )

    # ------------------------------------------------
    # APPLY FILTERS BUTTON
    # ------------------------------------------------

    st.markdown(
        '<div class="filter-button-container">',
        unsafe_allow_html=True
    )

    apply_filters = st.button(
        "🔎 Apply Filters",
        key="apply_filters",
        use_container_width=False
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # ------------------------------------------------
    # RESET BUTTON
    # ------------------------------------------------

    st.markdown(
        '<div class="reset-button-container">',
        unsafe_allow_html=True
    )

    reset_filters = st.button(
        "↻ Reset Filters",
        key="reset_filters"
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # ------------------------------------------------
    # CREATE FILTERED DATAFRAME
    # ------------------------------------------------

    filtered_df = df.copy()

    if apply_filters:

        if selected_hotel != "All Hotels":
            filtered_df = filtered_df[
                filtered_df["hotel"] == selected_hotel
            ]

        if selected_year != "All Years":
            filtered_df = filtered_df[
                filtered_df["arrival_date_year"] == selected_year
            ]

        if selected_month != "All Months":
            filtered_df = filtered_df[
                filtered_df["arrival_date_month"] == selected_month
            ]

        if selected_customer != "All Customer Types":
            filtered_df = filtered_df[
                filtered_df["customer_type"] == selected_customer
            ]

        if selected_market != "All Market Segments":
            filtered_df = filtered_df[
                filtered_df["market_segment"] == selected_market
            ]

        if selected_channel != "All Channels":
            filtered_df = filtered_df[
                filtered_df["distribution_channel"] == selected_channel
            ]

        if selected_deposit != "All Deposit Types":
            filtered_df = filtered_df[
                filtered_df["deposit_type"] == selected_deposit
            ]

        if selected_cancellation == "Confirmed Only":
            filtered_df = filtered_df[
                filtered_df["is_canceled"] == 0
            ]

        elif selected_cancellation == "Cancelled Only":
            filtered_df = filtered_df[
                filtered_df["is_canceled"] == 1
            ]

        if selected_repeat == "New Guests":
            filtered_df = filtered_df[
                filtered_df["is_repeated_guest"] == 0
            ]

        elif selected_repeat == "Repeat Guests":
            filtered_df = filtered_df[
                filtered_df["is_repeated_guest"] == 1
            ]

    # ------------------------------------------------
    # RESET
    # ------------------------------------------------

    if reset_filters:
        st.session_state["filter_hotel"] = "All Hotels"
        st.session_state["filter_year"] = "All Years"
        st.session_state["filter_month"] = "All Months"
        st.session_state["filter_customer"] = "All Customer Types"
        st.session_state["filter_market"] = "All Market Segments"
        st.session_state["filter_channel"] = "All Channels"
        st.session_state["filter_deposit"] = "All Deposit Types"
        st.session_state["filter_cancellation"] = "All Bookings"
        st.session_state["filter_repeat"] = "All Guests"

        st.rerun()

    return filtered_df

#====================================================================================
# ANALYSIS SECTION
#====================================================================================


