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
# Global CSS
# -------------------------------------------------
st.markdown("""
<style>
.stApp { background-color:#FFE5D4; color:black; }
h1,h2,h3,h4,h5,h6,p,span,label { color:black !important; }
input,textarea { background-color:white !important; color:black !important; }
.stSelectbox div[data-baseweb="select"]>div { background-color:white !important; }
.stDateInput input,.stNumberInput input { background-color:white !important; }
button { color:black !important; font-weight:600; }
</style>
""", unsafe_allow_html=True)

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
# Defects master
# -------------------------------------------------
DEFECTS = {
    "SH/SD": ["IRON PARTICALS", "BODY HOLE", "BODY DUST", "R&D (Low MOR)", "STAIN PROBLEM"],
    "Press": ["LAMINATION", "CONTAMINATION", "CENTER CRACK", "SIDE CRACK", "DIPRESSION",
              "DUST", "DEPRESSION", "MIS PATTERN", "WEDGING", "Grid Mark",
              "CHIPS PROBLEM", "SMALL SIZE", "BUMP"],
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
# Session state
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
# Save CSV
# -------------------------------------------------
def save_to_csv(batch, defects, bad, total):
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
                    "Size": batch.get("size"),
                    "Surface": batch.get("surface"),
                    "Department": dept,
                    "Defect": defect,
                    "Qty": qty,
                    "Defective Tiles": bad,
                    "Total Tiles": total
                })

    if not rows:
        return

    df = pd.DataFrame(rows)
    os.makedirs("data", exist_ok=True)
    df.to_csv(CSV_PATH, mode="a", header=not os.path.exists(CSV_PATH), index=False)

# -------------------------------------------------
# SCREEN 1: DASHBOARD (icons added ✅)
# -------------------------------------------------
if st.session_state.page == "dashboard":

    st.markdown(
        f"""
        <div style="background:white;padding:18px 24px;border-radius:12px;
                    box-shadow:0 3px 10px rgba(0,0,0,0.15);
                    display:flex;gap:16px;align-items:center;">
            <img src="data:image/png;base64,{LOGO}" height="50"/>
            <div>
                <div style="font-size:22px;font-weight:700;">🧱 SIPL Sorting Defect Report</div>
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
        st.markdown("### 🧾 Defect Reports")
        st.caption("Create and update defect batch records")
        if st.button("🧾 Open Defect Reports", use_container_width=True):
            st.session_state.page = "batch"

    with col2:
        st.markdown("### 📊 Download Defect History")
        st.caption("Export saved data as Excel (CSV)")
        if os.path.exists(CSV_PATH):
            with open(CSV_PATH, "rb") as f:
                st.download_button(
                    "📊 Download CSV",
                    f,
                    "defect_history.csv",
                    use_container_width=True
                )
        else:
            st.info("No defect history yet")

# -------------------------------------------------
# Remaining screens unchanged (stable)
# -------------------------------------------------
elif st.session_state.page == "batch":
    st.subheader("Batch Data")
    st.session_state.batch["date"] = st.date_input("Production Date")
    st.session_state.batch["shift"] = st.selectbox("Shift", ["Day", "Night"])
    st.session_state.batch["operator"] = st.text_input("Operator")
    st.session_state.batch["item_code"] = st.text_input("Item / SAP Code")
    st.session_state.batch["batch_code"] = st.text_input("Batch / SAP Batch")
    st.session_state.batch["size"] = st.text_input("Tile Size (e.g. 600×600)")
    st.session_state.batch["surface"] = st.selectbox("Surface", ["Matt", "Polished", "Glossy", "Satin", "Other"])
    if st.button("Confirm & Enter Defects"):
        st.session_state.page = "departments"

elif st.session_state.page == "departments":
    st.subheader("Departments")
    if st.button("Finish"):
        st.session_state.page = "summary"
    for dept in DEFECTS:
        total = sum(st.session_state.defects[dept].values())
        if st.button(f"{dept} | Defects: {total}"):
            st.session_state.current_dept = dept
            st.session_state.page = "defect_entry"

elif st.session_state.page == "defect_entry":
    dept = st.session_state.current_dept
    st.subheader(dept)
    if st.button("Back"):
        st.session_state.page = "departments"
    for defect in DEFECTS[dept]:
        c1, c2, c3 = st.columns([1,1,1])
        if c1.button("➖", key=f"{dept}{defect}m"):
            st.session_state.defects[dept][defect] = max(0, st.session_state.defects[dept][defect] - 1)
        c2.write(st.session_state.defects[dept][defect])
        if c3.button("➕", key=f"{dept}{defect}p"):
            st.session_state.defects[dept][defect] += 1

elif st.session_state.page == "summary":
    st.subheader("Summary")
    bad = st.number_input("Defective Tiles", min_value=0)
    total = st.number_input("Total Tiles", min_value=1)
    if st.button("Save") and not st.session_state.saved:
        save_to_csv(st.session_state.batch, st.session_state.defects, bad, total)
        st.session_state.saved = True
    if st.session_state.saved:
        st.success("Saved successfully")
        if st.button("Go to Dashboard"):
            st.session_state.page = "dashboard"
            st.session_state.saved = False
            st.session_state.batch = {}
            st.session_state.defects = {d: {k: 0 for k in DEFECTS[d]} for d in DEFECTS}
``
