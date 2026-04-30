import streamlit as st
import pandas as pd
from datetime import datetime
import os

# -------------------------------------------------
# App configuration
# -------------------------------------------------
st.set_page_config(
    page_title="Defect Batch Reporting",
    layout="wide"
)

# -------------------------------------------------
# Defect master
# -------------------------------------------------
DEFECTS = {
    "SH/SD": [
        "IRON PARTICALS", "BODY HOLE", "BODY DUST",
        "R&D (Low MOR)", "STAIN PROBLEM"
    ],
    "Press": [
        "LAMINATION", "CONTAMINATION", "CENTER CRACK",
        "SIDE CRACK", "DIPRESSION", "DUST",
        "DEPRESSION", "MIS PATTERN", "WEDGING",
        "Grid Mark", "CHIPS PROBLEM", "SMALL SIZE",
        "BUMP"
    ],
    "G/L": [
        "DUST", "BLACK DUST", "COLOUR DROP", "COLOUR SPOT",
        "GLAZE DROP", "DIMPLE", "FLOW CUT", "FACE HOLE",
        "DIGITAL LINING", "DIGITAL MIS PRINT",
        "GLAZE CRACK", "PIN HOLE", "T.R PROBLEM",
        "WATER DROP", "WHITE SPOT", "LUMPS",
        "CONTAMINATION", "APPLICATION PROBLEM",
        "GLAZE STICKING", "HEAD MARK", "BUBBLES",
        "SCRAPHER DUST"
    ],
    "Kiln": [
        "DUST", "DUST STECKING", "BEND", "SIDE CRACK",
        "OVER FIRED", "SURFACE CRACK", "IRON PARTICALS",
        "CHIPPING", "PIN HOLE", "BODY CRACK",
        "SHADE VARIATION", "WAVINESS", "FACE HOLE",
        "ROLLER DUST", "BUMP", "GRANULLA",
        "BUBBLES", "SULPHUR"
    ],
    "Polishing": [
        "SCRATCHES", "CHAMFERING", "CORNER CHIPPING",
        "SIDE CHIPPING", "WASH OUT", "CROSS CUTTING",
        "POLISHING CHIPPING", "MIS POLISH",
        "DULL POLISHING", "DIAGONAL", "CORNER BROKEN",
        "SIZE VARIATION", "CHEMICAL SPOT", "ROUGH CUT",
        "LOAD CRACK", "OUT CUTTING", "NANO STAIN",
        "MARKER PROBLRM", "POROSITY",
        "REPOLISHING CHIPPING", "WAVINESS",
        "PATTA", "RANTIC CRACK", "MACHING MIS"
    ],
    "General": [
        "SAMPLE", "BROKEN", "R AND D SAMPLE",
        "GRANULLA PROBLEM", "STANDARD PROD.", "QA CHIPPING"
    ]
}

CSV_PATH = "data/defect_history.csv"

# -------------------------------------------------
# Session state initialization
# -------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

if "batch" not in st.session_state:
    st.session_state.batch = {}

if "defects" not in st.session_state:
    st.session_state.defects = {
        dept: {d: 0 for d in DEFECTS[dept]}
        for dept in DEFECTS
    }

# -------------------------------------------------
# CSV save function
# -------------------------------------------------
def save_to_csv(batch, defects, defective_tiles, total_tiles):
    rows = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for dept, defect_map in defects.items():
        for defect, qty in defect_map.items():
            if qty > 0:
                rows.append({
                    "Timestamp": timestamp,
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
# Dashboard
# -------------------------------------------------
if st.session_state.page == "dashboard":
    st.title("📊 Dashboard")

    if st.button("📋 Defect Reports"):
        st.session_state.page = "batch"

    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, "rb") as f:
            st.download_button(
                "⬇ Download Defect History (CSV)",
                f,
                file_name="defect_history.csv"
            )

# -------------------------------------------------
# Batch data page
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
# Departments hub
# -------------------------------------------------
elif st.session_state.page == "departments":
    st.subheader("Departments")

    if st.button("✅ Finish", type="primary"):
        st.session_state.page = "summary"

    cols = st.columns(3)
    i = 0

    for dept in DEFECTS:
        total = sum(st.session_state.defects[dept].values())
        if cols[i].button(
            f"{dept}\nDefects: {total}",
            use_container_width=True
        ):
            st.session_state.current_dept = dept
            st.session_state.page = "defect_entry"
        i = (i + 1) % 3

# -------------------------------------------------
# Defect entry page
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
                st.session_state.defects[dept][defect] = max(
                    0, st.session_state.defects[dept][defect] - 1
                )

            c2.markdown(
                str(st.session_state.defects[dept][defect]),
                unsafe_allow_html=True
            )

            if c3.button("➕", key=f"p-{dept}-{defect}"):
                st.session_state.defects[dept][defect] += 1

# -------------------------------------------------
# Summary & save page
# -------------------------------------------------
elif st.session_state.page == "summary":
    st.subheader("Batch Summary")

    defective_tiles = st.number_input(
        "Number of defected tiles",
        min_value=0
    )
    total_tiles = st.number_input(
        "Total tiles in batch",
        min_value=1
    )

    if st.button("💾 Save"):
        save_to_csv(
            st.session_state.batch,
            st.session_state.defects,
            defective_tiles,
            total_tiles
        )
        st.success("✅ Data saved successfully")
        st.session_state.page = "dashboard"
