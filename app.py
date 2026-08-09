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
    "<h1 style='text-align: center; text-transform: uppercase; color: white; font-weight: 700; font-size: 64px;'>Hotel Booking Insights Dashboard</h1>",
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