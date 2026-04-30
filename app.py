import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64

# -------------------------------------------------
# Page configuration
# -------------------------------------------------
st.set_page_config(page_title="SIPL Sorting Defect Report", layout="wide")

# -------------------------------------------------
# Peach background (all screens)
# -------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #FFE5D4;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# Defect Master
# -------------------------------------------------
DEFECTS = {
    "SH/SD": ["IRON PARTICALS", "BODY HOLE", "BODY DUST", "R&D (Low MOR)", "STAIN PROBLEM"],
    "Press": ["LAMINATION", "CONTAMINATION", "CENTER CRACK", "SIDE CRACK", "DIPRESSION",
              "DUST", "DEPRESSION", "MIS PATTERN", "WEDGING", "Grid Mark",
              "CHIPS PROBLEM", "SMALL SIZE", "BUMP"],
    "G/L": ["DUST", "BLACK DUST", "COLOUR DROP", "COLOUR SPOT", "GLAZE DROP", "DIMPLE",
            "FLOW CUT", "FACE HOLE", "DIGITAL LINING", "DIGITAL MIS PRINT",
            "GLAZE CRACK", "PIN HOLE", "T.R PROBLEM", "WATER DROP", "WHITE SPOT",
            "LUMPS", "CONTAMINATION", "APPLICATION PROBLEM", "GLAZE STICKING",
            "HEAD MARK", "BUBBLES", "SCRAPHER DUST"],
    "Kiln": ["DUST", "DUST STECKING", "BEND", "SIDE CRACK", "OVER FIRED",
             "SURFACE CRACK", "IRON PARTICALS", "CHIPPING", "PIN HOLE",
             "BODY CRACK", "SHADE VARIATION", "WAVINESS", "FACE HOLE",
             "ROLLER DUST", "BUMP", "GRANULLA", "BUBBLES", "SULPHUR"],
    "Polishing": ["SCRATCHES", "CHAMFERING", "CORNER CHIPPING", "SIDE CHIPPING",
                  "WASH OUT", "CROSS CUTTING", "POLISHING CHIPPING", "MIS POLISH",
                  "DULL POLISHING", "DIAGONAL", "CORNER BROKEN", "SIZE VARIATION",
                  "CHEMICAL SPOT", "ROUGH CUT", "LOAD CRACK", "OUT CUTTING",
                  "NANO STAIN", "MARKER PROBLRM", "POROSITY",
                  "REPOLISHING CHIPPING", "WAVINESS", "PATTA",
                  "RANTIC CRACK", "MACHING MIS"],
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
    st.session_state.defects = {dept: {d: 0 for d in DEFECTS[dept]} for dept in DEFECTS}

if "saved" not in st.session_state:
    st.session_state.saved = False

# -------------------------------------------------
# Utility: Load logo as base64
# -------------------------------------------------
def load_logo():
    if os.path.exists("logo.png"):
        return base64.b64encode(open("logo.png", "rb").read()).decode()
    return ""

logo_base64 = load_logo()

# -------------------------------------------------
# CSV Save
# -------------------------------------------------
def save_to_csv(batch, defects, defective_tiles, total_tiles):
    rows = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for dept, defect_map in defects.items():
        for defect, qty in defect_map.items():
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
                    "Defective Tiles": defective_tiles,
                    "Total Tiles": total_tiles
                })

    if not rows:
        return

    df = pd.DataFrame(rows)
    os.makedirs("data", exist_ok=True)

    if os.path.exists(CSV_PATH):
        df.to_csv(CSV_PATH, mode="a", header=False, index=False)
    else:
        df.to_csv(CSV_PATH, index=False)

# -------------------------------------------------
# SCREEN 1: DASHBOARD
# -------------------------------------------------
if st.session_state.page == "dashboard":

    # Header bar
    st.markdown(
        f"""
        <div style="background:#ffffff;
                    padding:15px 25px;
                    border-radius:12px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.12);
                    margin-bottom:25px;
                    display:flex;
                    align-items:center;
                    justify-content:space-between;">

            <div style="display:flex; align-items:center; gap:15px;">
                <img src="data:image/png;base64,{logo_base64}" style="height:45px;">
                <div>
                    <div style="font-size:22px; font-weight:700;">
                        SIPL Sorting Defect Report
                    </div>
                    <div style="font-size:13px; opacity:0.7;">
                        Home — choose an area below
                    </div>
                </div>
            </div>

            <div>
                <span style="background:#dc3545;
                             color:white;
                             padding:8px 14px;
                             border-radius:6px;
                             font-size:12px;">
                    Logout
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("## 🎛 Dashboard")
    st.markdown("### Select an option to continue")
    st.markdown("---")

    col1, col2 = st.columns(2)

    # Left card
    with col1:
        st.markdown(
            """
            <div style="background:#ffffff;
                        border-radius:16px;
                        padding:30px;
                        height:240px;
                        text-align:center;
                        box-shadow:0 4px 10px rgba(0,0,0,0.1);">
                <div style="font-size:64px;">📋</div>
                <h3>Defect Reports</h3>
                <p>Create and update defect batch records</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Open Defect Reports", use_container_width=True):
            st.session_state.page = "batch"

    # Right card
    with col2:
        st.markdown(
            """
            <div style="background:#ffffff;
                        border-radius:16px;
                        padding:30px;
                        height:240px;
                        text-align:center;
                        box-shadow:0 4px 10px rgba(0,0,0,0.1);">
                <div style="font-size:64px;">⬇</div>
                <h3>Download Defect History</h3>
                <p>Export saved data as CSV</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if os.path.exists(CSV_PATH):
            with open(CSV_PATH, "rb") as f:
                st.download_button("Download CSV", f, "defect_history.csv", use_container_width=True)
        else:
            st.info("No defect history yet")

# -------------------------------------------------
# SCREEN 2: BATCH DATA
# -------------------------------------------------
elif st.session_state.page == "batch":
    st.subheader("Batch Data")

    st.session_state.batch["date"] = st.date_input("Production Date")
    st.session_state.batch["shift"] = st.selectbox("Shift", ["Day", "Night"])
    st.session_state.batch["operator"] = st.text_input("Operator")
    st.session_state.batch["item_code"] = st.text_input("Item / SAP Code")
    st.session_state.batch["batch_code"] = st.text_input("Batch / SAP Batch")

    if st.button("Confirm & Enter Defects"):
        st.session_state.page = "departments"

# -------------------------------------------------
# SCREEN 3: DEPARTMENTS
# -------------------------------------------------
elif st.session_state.page == "departments":
    st.subheader("Departments")

    if st.button("✅ Finish", type="primary"):
        st.session_state.page = "summary"

    cols = st.columns(3)
    i = 0
    for dept in DEFECTS:
        total = sum(st.session_state.defects[dept].values())
        if cols[i].button(f"{dept}\nDefects: {total}", use_container_width=True):
            st.session_state.current_dept = dept
            st.session_state.page = "defect_entry"
        i = (i + 1) % 3

# -------------------------------------------------
# SCREEN 4: DEFECT ENTRY
# -------------------------------------------------
elif st.session_state.page == "defect_entry":
    dept = st.session_state.current_dept
    st.subheader(f"{dept} – Defects")

    if st.button("⬅ Back to Departments"):
        st.session_state.page = "departments"

    cols = st.columns(3)
    for i, defect in enumerate(DEFECTS[dept]):
        with cols[i % 3]:
            st.markdown(f"**{defect}**")
            c1, c2, c3 = st.columns([1, 1, 1])
            if c1.button("➖", key=f"m-{dept}-{defect}"):
                st.session_state.defects[dept][defect] = max(0, st.session_state.defects[dept][defect] - 1)
            c2.markdown(st.session_state.defects[dept][defect])
            if c3.button("➕", key=f"p-{dept}-{defect}"):
                st.session_state.defects[dept][defect] += 1

# -------------------------------------------------
# SCREEN 5: SUMMARY & SAVE
# -------------------------------------------------
elif st.session_state.page == "summary":
    st.subheader("Batch Summary")

    defective_tiles = st.number_input("Number of defected tiles", min_value=0)
    total_tiles = st.number_input("Total tiles in batch", min_value=1)

    if st.button("💾 Save") and not st.session_state.saved:
        save_to_csv(st.session_state.batch, st.session_state.defects, defective_tiles, total_tiles)
        st.session_state.saved = True

    if st.session_state.saved:
        st.success("✅ Data saved successfully")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔙 Go to Dashboard", use_container_width=True):
                st.session_state.page = "dashboard"
                st.session_state.saved = False
                st.session_state.batch = {}
                st.session_state.defects = {dept: {d: 0 for d in DEFECTS[dept]} for dept in DEFECTS}

        with col2:
            st.info("You may safely close the app now")
