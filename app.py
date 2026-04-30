import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="SIPL Sorting Defect Report",
    layout="wide"
)

# ================= SIMPLE THEME =================
st.markdown("""
<style>
.stApp { background-color:#FFE5D4; }
input, textarea { background-color:white !important; }
button { font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ================= DEFECT MASTER =================
DEFECTS = {
    "SH/SD": ["IRON PARTICALS", "BODY HOLE", "BODY DUST", "R&D (Low MOR)", "STAIN PROBLEM"],
    "Press": ["LAMINATION", "CONTAMINATION", "CENTER CRACK", "SIDE CRACK", "DIPRESSION",
              "DUST", "DEPRESSION", "MIS PATTERN", "WEDGING", "Grid Mark",
              "CHIPS PROBLEM", "SMALL SIZE", "BUMP"],
    "G/L": ["DUST", "BLACK DUST", "COLOUR DROP", "COLOUR SPOT", "GLAZE DROP",
            "DIMPLE", "FLOW CUT", "FACE HOLE", "DIGITAL LINING",
            "DIGITAL MIS PRINT", "GLAZE CRACK", "PIN HOLE",
            "T.R PROBLEM", "WATER DROP", "WHITE SPOT",
            "CONTAMINATION", "APPLICATION PROBLEM", "GLAZE STICKING",
            "HEAD MARK", "BUBBLES"],
    "Kiln": ["DUST", "BEND", "SIDE CRACK", "OVER FIRED",
             "SURFACE CRACK", "IRON PARTICALS", "CHIPPING",
             "PIN HOLE", "BODY CRACK", "SHADE VARIATION", "WAVINESS"],
    "Polishing": ["SCRATCHES", "CHAMFERING", "CORNER CHIPPING",
                  "SIDE CHIPPING", "WASH OUT", "MIS POLISH",
                  "DULL POLISHING", "SIZE VARIATION", "LOAD CRACK"],
    "General": ["SAMPLE", "BROKEN", "R AND D SAMPLE", "QA CHIPPING"]
}

CSV_PATH = "data/defect_history.csv"

# ================= SESSION STATE =================
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "batch" not in st.session_state:
    st.session_state.batch = {}
if "defects" not in st.session_state:
    st.session_state.defects = {d:{k:0 for k in DEFECTS[d]} for d in DEFECTS}
if "saved" not in st.session_state:
    st.session_state.saved = False

# ================= SAVE TO CSV =================
def save_to_csv(batch, defects, bad_tiles, total_tiles):
    rows = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for dept, items in defects.items():
        for defect, qty in items.items():
            if qty > 0:
                rows.append({
                    "Timestamp": ts,
                    "Date": batch["date"],
                    "Shift": batch["shift"],
                    "Operator": batch["operator"],
                    "Item": batch["item_code"],
                    "Batch": batch["batch_code"],
                    "Size": batch["size"],
                    "Surface": batch["surface"],
                    "Department": dept,
                    "Defect": defect,
                    "Qty": qty,
                    "Defective Tiles": bad_tiles,
                    "Total Tiles": total_tiles
                })

    if not rows:
        return

    os.makedirs("data", exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(CSV_PATH, mode="a", header=not os.path.exists(CSV_PATH), index=False)

# ================= SCREEN 1 =================
if st.session_state.page == "dashboard":
    st.title("SIPL Sorting Defect Report")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ New Defect Batch", use_container_width=True):
            st.session_state.page = "batch"
    with col2:
        if os.path.exists(CSV_PATH):
            with open(CSV_PATH, "rb") as f:
                st.download_button("📊 Download CSV", f, "defect_history.csv",
                                   use_container_width=True)

# ================= SCREEN 2 =================
elif st.session_state.page == "batch":
    st.header("Batch Details")

    st.session_state.batch["date"] = st.date_input("Production Date")
    st.session_state.batch["shift"] = st.selectbox("Shift", ["Day", "Night"])
    st.session_state.batch["operator"] = st.text_input("Operator")
    st.session_state.batch["item_code"] = st.text_input("Item / SAP Code")
    st.session_state.batch["batch_code"] = st.text_input("Batch Code")
    st.session_state.batch["size"] = st.text_input("Tile Size (e.g. 600×600)")
    st.session_state.batch["surface"] = st.selectbox(
        "Surface", ["Matt", "Polished", "Glossy", "Satin", "Other"]
    )

    if st.button("Continue"):
        st.session_state.page = "departments"

# ================= SCREEN 3 (3×2 GRID) =================
elif st.session_state.page == "departments":
    st.header("Select Department")

    icons = {
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
        for i, dept in enumerate(row):
            with cols[i]:
                total = sum(st.session_state.defects[dept].values())
                st.markdown(f"### {icons[dept]} {dept}")
                st.caption(f"Defects: {total}")
                if st.button("Open", key=dept, use_container_width=True):
                    st.session_state.current_dept = dept
                    st.session_state.page = "defect_entry"

    if st.button("Finish"):
        st.session_state.page = "summary"

# ================= SCREEN 4 (DEFECT ENTRY) =================
elif st.session_state.page == "defect_entry":
    dept = st.session_state.current_dept
    st.header(f"{dept} Defects")

    if st.button("⬅ Back"):
        st.session_state.page = "departments"

    for defect in DEFECTS[dept]:
        c1, c2, c3 = st.columns([1,1,1])

        if c1.button("➖", key=f"{dept}_{defect}_m"):
            st.session_state.defects[dept][defect] = max(
                0, st.session_state.defects[dept][defect] - 1
            )

        c2.markdown(f"### {st.session_state.defects[dept][defect]}")
        c2.caption(defect)

        if c3.button("➕", key=f"{dept}_{defect}_p"):
            st.session_state.defects[dept][defect] += 1

# ================= SCREEN 5 =================
elif st.session_state.page == "summary":
    st.header("Summary")

    bad_tiles = st.number_input("Defective Tiles", min_value=0)
    total_tiles = st.number_input("Total Tiles", min_value=1)

    if st.button("Save"):
        save_to_csv(
            st.session_state.batch,
            st.session_state.defects,
            bad_tiles,
            total_tiles
        )
        st.success("✅ Saved Successfully")
        st.session_state.page = "dashboard"
        st.session_state.batch = {}
        st.session_state.defects = {d:{k:0 for k in DEFECTS[d]} for d in DEFECTS}
