import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="SIPL Sorting Defect Report",
    layout="wide"
)

# =========================
# GLOBAL CSS
# =========================
st.markdown("""
<style>
.stApp {
    background-color: #FFE5D4;
    color: black;
}
h1, h2, h3, h4, h5, h6, p, span, label {
    color: black !important;
}
input, textarea, select {
    background-color: white !important;
    color: black !important;
}
button {
    color: black !important;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# =========================
# LOAD LOGO
# =========================
def load_logo_base64():
    if os.path.exists("logo.png"):
        with open("logo.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

LOGO = load_logo_base64()

# =========================
# DEFECT MASTER
# =========================
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

# =========================
# SESSION STATE
# =========================
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "batch" not in st.session_state:
    st.session_state.batch = {}
if "defects" not in st.session_state:
    st.session_state.defects = {d: {k: 0 for k in DEFECTS[d]} for d in DEFECTS}
if "saved" not in st.session_state:
    st.session_state.saved = False

# =========================
# SAVE TO CSV
# =========================
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
                    "Size": batch.get("size"),          # ✅ added
                    "Surface": batch.get("surface"),    # ✅ added
                    "Department": dept,
                    "Defect": defect,
                    "Qty": qty,
                    "Defective Tiles": bad_tiles,
                    "Total Tiles": total_tiles
                })

    if rows:
        os.makedirs("data", exist_ok=True)
        pd.DataFrame(rows).to_csv(
            CSV_PATH, mode="a",
            header=not os.path.exists(CSV_PATH),
            index=False
        )

# =========================
# SCREEN 1: DASHBOARD (LOGO FIXED ✅)
# =========================
if st.session_state.page == "dashboard":

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:16px;
                background:white;padding:18px 24px;border-radius:12px;
                box-shadow:0 3px 10px rgba(0,0,0,0.15);margin-bottom:25px;">
        <img src="data:image/png;base64,{LOGO}" height="60">
        <div>
            <div style="font-size:22px;font-weight:700;">SIPL Sorting Defect Report</div>
            <div style="font-size:13px;">Home — choose an area below</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.header("🎛 Dashboard")
    st.subheader("Select an option to continue")
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Open Defect Reports", use_container_width=True):
            st.session_state.page = "batch"

    with col2:
        if os.path.exists(CSV_PATH):
            with open(CSV_PATH, "rb") as f:
                st.download_button("Download CSV", f, "defect_history.csv", use_container_width=True)

# =========================
# SCREEN 2: BATCH DATA (SIZE + SURFACE ✅)
# =========================
elif st.session_state.page == "batch":
    st.subheader("Batch Data")

    st.session_state.batch["date"] = st.date_input("Production Date")
    st.session_state.batch["shift"] = st.selectbox("Shift", ["Day", "Night"])
    st.session_state.batch["operator"] = st.text_input("Operator")
    st.session_state.batch["item_code"] = st.text_input("Item / SAP Code")
    st.session_state.batch["batch_code"] = st.text_input("Batch / SAP Batch")

    st.session_state.batch["size"] = st.text_input("Tile Size (e.g. 600×600)")      # ✅ added
    st.session_state.batch["surface"] = st.selectbox(                                # ✅ added
        "Surface", ["Matt", "Polished", "Glossy", "Satin", "Other"]
    )

    if st.button("Confirm & Enter Defects"):
        st.session_state.page = "departments"

# =========================
# REMAINING SCREENS (UNCHANGED)
# =========================
elif st.session_state.page == "departments":
    st.subheader("Departments")
    cols = st.columns(3)
    i = 0
    for dept in DEFECTS:
        total = sum(st.session_state.defects[dept].values())
        if cols[i].button(f"{dept}\nDefects: {total}", use_container_width=True):
            st.session_state.current_dept = dept
            st.session_state.page = "defect_entry"
        i = (i + 1) % 3
    if st.button("Finish"):
        st.session_state.page = "summary"

elif st.session_state.page == "defect_entry":
    dept = st.session_state.current_dept
    st.subheader(f"{dept} – Defects")
    if st.button("⬅ Back to Departments"):
        st.session_state.page = "departments"

    cols = st.columns(3)
    for i, defect in enumerate(DEFECTS[dept]):
        with cols[i % 3]:
            st.markdown(f"**{defect}**")
            c1, c2, c3 = st.columns([1,1,1])
            if c1.button("➖", key=f"m-{dept}-{defect}"):
                st.session_state.defects[dept][defect] = max(0, st.session_state.defects[dept][defect] - 1)
            c2.markdown(st.session_state.defects[dept][defect])
            if c3.button("➕", key=f"p-{dept}-{defect}"):
                st.session_state.defects[dept][defect] += 1

elif st.session_state.page == "summary":
    st.subheader("Batch Summary")
    bad_tiles = st.number_input("Number of defected tiles", min_value=0)
    total_tiles = st.number_input("Total tiles in batch", min_value=1)
    if st.button("Save"):
        save_to_csv(st.session_state.batch, st.session_state.defects, bad_tiles, total_tiles)
        st.success("✅ Data saved successfully")
        st.session_state.page = "dashboard"
        st.session_state.batch = {}
        st.session_state.defects = {d: {k: 0 for k in DEFECTS[d]} for d in DEFECTS}

