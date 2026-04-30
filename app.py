import streamlit as st
import pandas CRACK",import pandas as pd
            "PIN HOLE", "T.R PROBLEM", "WATER DROP", "WHITE SPOT",
            "LUMPS", "CONTAMINATION", "APPLICATION PROBLEM",
            "GLAZE STICKING", "HEAD MARK", "BUBBLES", "SCRAPHER DUST"],
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

# ===================== SESSION STATE =====================
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "batch" not in st.session_state:
    st.session_state.batch = {}
if "defects" not in st.session_state:
    st.session_state.defects = {d: {k: 0 for k in DEFECTS[d]} for d in DEFECTS}
if "saved" not in st.session_state:
    st.session_state.saved = False

# ===================== SAVE CSV =====================
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
                    "Size": batch.get("size"),
                    "Surface": batch.get("surface"),
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

# ===================== SCREEN 1 =====================
if st.session_state.page == "dashboard":
    st.header("SIPL Sorting Defect Report")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧾 Add / Update Defect Report", use_container_width=True):
            st.session_state.page = "batch"
    with col2:
        if os.path.exists(CSV_PATH):
            with open(CSV_PATH, "rb") as f:
                st.download_button(
                    "📊 Download History (CSV)",
                    f,
                    "defect_history.csv",
                    use_container_width=True
                )

# ===================== SCREEN 2 =====================
elif st.session_state.page == "batch":
    st.subheader("Batch Details")

    st.session_state.batch["date"] = st.date_input("Production Date")
    st.session_state.batch["shift"] = st.selectbox("Shift", ["Day", "Night"])
    st.session_state.batch["operator"] = st.text_input("Operator")
    st.session_state.batch["item_code"] = st.text_input("Item / SAP Code")
    st.session_state.batch["batch_code"] = st.text_input("Batch Code")
    st.session_state.batch["size"] = st.text_input("Tile Size (e.g. 600x600)")
    st.session_state.batch["surface"] = st.selectbox(
        "Surface", ["Matt", "Polished", "Glossy", "Satin", "Other"]
    )

    if st.button("Continue to Departments"):
        st.session_state.page = "departments"

# ===================== SCREEN 3: DEPARTMENT GRID ✅ =====================
elif st.session_state.page == "departments":
    st.subheader("Select Department")

    if st.button("Finish"):
        st.session_state.page = "summary"

    dept_icons = {
        "SH/SD": "🏭",
        "Press": "🧱",
        "G/L": "🎨",
        "Kiln": "🔥",
        "Polishing": "✨",
        "General": "📦"
    }

    depts = list(DEFECTS.keys())
    rows = [depts[i:i+3] for i in range(0, 6, 3)]

    for row in rows:
        cols = st.columns(3)
        for idx, dept in enumerate(row):
            total = sum(st.session_state.defects[dept].values())
            with cols[idx]:
                st.markdown(f"### {dept_icons[dept]} {dept}")
                st.caption(f"Defects: {total}")
                if st.button(f"Open {dept}", key=f"dept_{dept}", use_container_width=True):
                    st.session_state.current_dept = dept
                    st.session_state.page = "defect_entry"

# ===================== SCREEN 4: DEFECT ENTRY (UNCHANGED ✅) =====================
elif st.session_state.page == "defect_entry":
    dept = st.session_state.current_dept
    st.subheader(f"{dept} Defects")

    if st.button("← Back to Departments"):
        st.session_state.page = "departments"

    for defect in DEFECTS[dept]:
        col1, col2, col3 = st.columns([1, 1, 1])

        if col1.button("➖", key=f"{dept}_{defect}_minus"):
            st.session_state.defects[dept][defect] = max(
                0, st.session_state.defects[dept][defect] - 1
            )

        col2.markdown(f"### {st.session_state.defects[dept][defect]}")
        col2.caption(defect)

        if col3.button("➕", key=f"{dept}_{defect}_plus"):
            st.session_state.defects[dept][defect] += 1

# ===================== SCREEN 5 =====================
elif st.session_state.page == "summary":
    st.subheader("Summary")

    bad_tiles = st.number_input("Total Defective Tiles", min_value=0)
    total_tiles = st.number_input("Total Tiles in Batch", min_value=1)

    if st.button("Save Report") and not st.session_state.saved:
        save_to_csv(
            st.session_state.batch,
            st.session_state.defects,
            bad_tiles,
            total_tiles
        )
        st.session_state.saved = True

    if st.session_state.saved:
        st.success("✅ Data saved successfully")
        if st.button("Back to Dashboard"):
            st.session_state.page = "dashboard"
            st.session_state.saved = False
            st.session_state.batch = {}
            st.session_state.defects = {
                d: {k: 0 for k in DEFECTS[d]} for d in DEFECTS
            }

from datetime import datetime
import os
import base64

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="SIPL Sorting Defect Report",
    layout="wide"
)

# ===================== BASIC THEME =====================
st.markdown("""
<style>
.stApp { background-color:#FFE5D4; color:black; }
input, textarea { background-color:white !important; }
button { font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ===================== LOAD LOGO =====================
def load_logo():
    if os.path.exists("logo.png"):
        with open("logo.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

LOGO = load_logo()

# ===================== DEFECT MASTER =====================
DEFECTS = {
    "SH/SD": ["IRON PARTICALS", "BODY HOLE", "BODY DUST", "R&D (Low MOR)", "STAIN PROBLEM"],
    "Press": ["LAMINATION", "CONTAMINATION", "CENTER CRACK", "SIDE CRACK",
              "DIPRESSION", "DUST", "DEPRESSION", "MIS PATTERN",
              "WEDGING", "Grid Mark", "CHIPS PROBLEM", "SMALL SIZE", "BUMP"],
    "G/L": ["DUST", "BLACK DUST", "COLOUR DROP", "COLOUR SPOT",
            "GLAZE DROP", "DIMPLE", "FLOW CUT", "FACE HOLE",
