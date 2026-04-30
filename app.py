import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(page_title="SIPL Sorting Defect Report", layout="wide")

# -------------------------------------------------
# Global CSS (ALL SCREENS)
# -------------------------------------------------
st.markdown(
    """
    <style>
    /* App background */
    .stApp {
        background-color: #FFE5D4;
        color: black;
    }

    /* All text black */
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: black !important;
    }

    /* Input fields white */
    input, textarea {
        background-color: white !important;
        color: black !important;
    }

    /* Select boxes */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: white !important;
        color: black !important;
    }

    /* Number input */
    .stNumberInput input {
        background-color: white !important;
        color: black !important;
    }

    /* Date input */
    .stDateInput input {
        background-color: white !important;
        color: black !important;
    }

    /* Buttons text black */
    button {
        color: black !important;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# Load logo
# -------------------------------------------------
def load_logo():
    if os.path.exists("logo.png"):
        with open("logo.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

LOGO = load_logo()

# -------------------------------------------------
# Defect Master
# -------------------------------------------------
DEFECTS = {
    "SH/SD": ["IRON PARTICALS", "BODY HOLE", "BODY DUST", "R&D (Low MOR)", "STAIN PROBLEM"],
    "Press": ["LAMINATION", "CONTAMINATION", "CENTER CRACK", "SIDE CRACK",
              "DIPRESSION", "DUST", "DEPRESSION", "MIS PATTERN",
              "WEDGING", "Grid Mark", "CHIPS PROBLEM", "SMALL SIZE", "BUMP"],
    "G/L": ["DUST", "BLACK DUST", "COLOUR DROP", "COLOUR SPOT", "GLAZE DROP",
            "DIMPLE", "FLOW CUT", "FACE HOLE", "DIGITAL LINING",
            "DIGITAL MIS PRINT", "GLAZE CRACK", "PIN HOLE",
            "T.R PROBLEM", "WATER DROP", "WHITE SPOT", "LUMPS",
            "CONTAMINATION", "APPLICATION PROBLEM", "GLAZE STICKING",
            "HEAD MARK", "BUBBLES", "SCRAPHER DUST"],
    "Kiln": ["DUST", "DUST STECKING", "BEND", "SIDE CRACK", "OVER FIRED",
             "SURFACE CRACK", "IRON PARTICALS", "CHIPPING",
             "PIN HOLE", "BODY CRACK", "SHADE VARIATION",
             "WAVINESS", "FACE HOLE", "ROLLER DUST", "BUMP",
             "GRANULLA", "BUBBLES", "SULPHUR"],
    "Polishing": ["SCRATCHES", "CHAMFERING", "CORNER CHIPPING",
                  "SIDE CHIPPING", "WASH OUT", "CROSS CUTTING",
                  "POLISHING CHIPPING", "MIS POLISH",
                  "DULL POLISHING", "DIAGONAL", "CORNER BROKEN",
                  "SIZE VARIATION", "CHEMICAL SPOT", "ROUGH CUT",
                  "LOAD CRACK", "OUT CUTTING", "NANO STAIN",
                  "MARKER PROBLRM", "POROSITY",
                  "REPOLISHING CHIPPING", "WAVINESS",
                  "PATTA", "RANTIC CRACK", "MACHING MIS"],
    "General": ["SAMPLE", "BROKEN", "R AND D SAMPLE",
                "GRANULLA PROBLEM", "STANDARD PROD.", "QA CHIPPING"]
}

CSV_PATH = "data/defect_history.csv"

# -------------------------------------------------
# Session State
# -------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

if "batch" not in st.session_state:
    st.session_state.batch = {}

if "defects" not in st.session_state:
    st.session_state.defects = {d: {k: 0 for k in DEFECTS[d]} for d in DEFECTS}

if "saved" not in st.session_state:
    st.session_state.saved = False

# -------------------------------------------------
# Save to CSV
# -------------------------------------------------
def save_to_csv(batch, defects, bad_tiles, total_tiles):
    rows = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for dept, items in defects.items():
        for defect, qty in items.items():
            if qty > 0:
                rows.append({
                    "Timestamp": ts,
                    "Date": batch.get("date"),
                    "Shift": batch.get("shift"),
                    "Operator": batch.get("operator"),
                    "Item": batch.get("item_code"),
                    "Batch": batch.get("batch_code"),
                    "Department": dept,
                    "Defect": defect,
                    "Qty": qty,
                    "Defective Tiles": bad_tiles,
                    "Total Tiles": total_tiles
                })

    if not rows:
        return

    df = pd.DataFrame(rows)
    os.makedirs("data", exist_ok=True)
    df.to_csv(CSV_PATH, mode="a", header=not os.path.exists(CSV_PATH), index=False)

# -------------------------------------------------
# SCREEN 1: DASHBOARD
# -------------------------------------------------
if st.session_state.page == "dashboard":

    st.markdown(
        f"""
        <div style="background:white;
                    padding:16px 24px;
                    border-radius:12px;
                    box-shadow:0 3px 10px rgba(0,0,0,0.15);
                    display:flex;
                    align-items:center;
                    gap:15px;
                    margin-bottom:25px;">
            <img src="data:image/png;base64,{LOGO}" height="45"/>
            <div>
                <div style="font-size:22px;font-weight:700;">SIPL Sorting Defect Report</div>
                <div style="font-size:13px;opacity:0.7;">Home — choose an area below</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.header("🎛 Dashboard")
    st.subheader("Select an option to continue")
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div style="background:white;border-radius:16px;
                        padding:30px;height:240px;
                        box-shadow:0 4px 10px rgba(0,0,0,0.1);
                        text-align:center;">
                <div style="font-size:64px;">📋</div>
                <h3>Defect Reports</h3>
                <p>Create & update defect batches</p>
            </div>
            """, unsafe_allow_html=True
        )
        if st.button("Open Defect Reports", use_container_width=True):
            st.session_state.page = "batch"

    with col2:
        st.markdown(
            """
            <div style="background:white;border-radius:16px;
                        padding:30px;height:240px;
                        box-shadow:0 4px 10px rgba(0,0,0,0.1);
                        text-align:center;">
                <div style="font-size:64px;">📊</div>
                <h3>Download Defect History</h3>
                <p>Export data as Excel (CSV)</p>
            </div>
            """, unsafe_allow_html=True
        )
        if os.path.exists(CSV_PATH):
            with open(CSV_PATH, "rb") as f:
                st.download_button(
                    "📊 Download CSV",
                    f,
                    file_name="defect_history.csv",
                    use_container_width=True
                )
        else:
            st.info("No defect history yet")

# -------------------------------------------------
# Remaining screens (Batch, Department, Defects, Summary)
# (UI colors already handled globally)
# -------------------------------------------------

# 👉 Your existing logic remains unchanged below
# (No functional change required)
