#====================================================================================
# IMPORT LIBRARY
#====================================================================================

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

st.markdown(
    "<h1 style='text-align: center; text-transform: uppercase; color: white; font-weight: 700; font-size: 64px;'>Hotel Booking Analytics Dashboard</h1>",
    unsafe_allow_html=True,
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
    type=["csv"],
)

if uploaded_file is not None:
    st.session_state["uploaded_file"] = uploaded_file
    st.success("📄 Dataset selected. Click below to begin preparation.")

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
        popup_placeholder = st.empty()

        def render_preparation_popup(step_index, total_steps, status, detail, title="Preparing your dataset", current_step_name=None):
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
            popup_placeholder.markdown(html, unsafe_allow_html=True)

        # ----------------------------------------------------
        # READ DATA
        # ----------------------------------------------------

        try:
            selected_file = st.session_state.get("uploaded_file", uploaded_file)
            selected_file.seek(0)
            df = pd.read_csv(
                selected_file,
                encoding="utf-8",
                encoding_errors="replace",
                low_memory=False,
            )
        except Exception:
            try:
                selected_file.seek(0)
                df = pd.read_csv(
                    selected_file,
                    encoding="latin-1",
                    low_memory=False,
                )
            except Exception as e:
                st.error("❌ Could not read the uploaded CSV file.")
                st.code(str(e))
                st.info(
                    "Please make sure the uploaded file is a valid CSV and uses the expected Hotel Booking dataset format."
                )
                st.stop()

        try:
            render_preparation_popup(0, 5, "running", "Checking that all required columns are present.", current_step_name="Validate required columns")
            time.sleep(0.4)

            original_df = df.copy()
            original_rows = len(df)
            original_columns = len(df.columns)

            dataset_columns = set(df.columns)
            missing_columns = [column for column in REQUIRED_COLUMNS if column not in dataset_columns]

            if missing_columns:
                render_preparation_popup(0, 5, "error", f"Missing columns detected: {', '.join(missing_columns)}", current_step_name="Validate required columns")
                st.error("❌ Dataset validation failed.")
                st.write("The following required columns are missing:")
                for column in missing_columns:
                    st.write(f"❌ `{column}`")
                st.stop()

            render_preparation_popup(0, 5, "success", f"All {len(REQUIRED_COLUMNS)} required columns are available.", current_step_name="Validate required columns")
            time.sleep(0.4)

            render_preparation_popup(1, 5, "running", "Checking the dataset for missing values.", current_step_name="Check missing values")
            time.sleep(0.4)

            missing_before = df.isnull().sum()
            total_missing_before = missing_before.sum()

            missing_table = missing_before[missing_before > 0].sort_values(ascending=False).to_frame("Missing Values")

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

            remaining_missing = df.isnull().sum().sum()
            remaining_duplicates = df.duplicated().sum()
            final_rows = len(df)

            st.session_state["cleaned_df"] = df
            st.session_state["original_df"] = original_df
            st.session_state["data_prepared"] = True

            render_preparation_popup(4, 5, "success", "Prepared successfully — now proceeding to analysis.", current_step_name="Finalize dataset")
            time.sleep(1.2)
            popup_placeholder.empty()

            st.markdown("## ✅ Data Preparation Complete")
            st.success("🎉 Your dataset has been prepared successfully and is ready for analysis.")

            st.markdown("## 📊 Cleaning Summary")
            summary_col1, summary_col2 = st.columns(2)

            with summary_col1:
                st.write(f"**Original Rows:** {original_rows:,}")
                st.write(f"**Duplicate Rows Removed:** {duplicates_before:,}")
                st.write(f"**Final Rows:** {final_rows:,}")

            with summary_col2:
                st.write(f"**Original Missing Values:** {total_missing_before:,}")
                st.write(f"**Remaining Missing Values:** {remaining_missing:,}")
                st.write(f"**Columns:** {original_columns}")

            st.markdown("## ✅ Final Data Validation")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Original Rows", f"{original_rows:,}")
            col2.metric("Final Rows", f"{final_rows:,}")
            col3.metric("Missing Values", f"{remaining_missing:,}")
            col4.metric("Duplicate Rows", f"{remaining_duplicates:,}")

            if remaining_missing == 0 and remaining_duplicates == 0:
                st.success("🎉 Data preparation completed successfully!")
            else:
                st.warning("⚠️ Some data quality issues still remain.")

            with st.expander("👀 Preview Cleaned Dataset"):
                st.dataframe(df.head(100), use_container_width=True)

        except Exception as e:
            render_preparation_popup(4, 5, "error", f"Preparation failed: {str(e)}", current_step_name="Finalize dataset")
            st.error("❌ Preparation failed.")
            st.code(str(e))
            st.stop()