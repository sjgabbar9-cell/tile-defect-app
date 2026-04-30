import streamlit as st
import pandas as pd
from datetime import datetime
import os

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="SIPL Sorting Defect Report",
    layout="wide"
)

# =========================
# GLOBAL STYLE (minimal & safe)
# =========================
st.markdown("""
<style>
.stApp {
    background-color: #FFE5D4;
}
input, textarea {
    background-color: white !important;
}
button {
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

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
                    "Size": batch.get("size"),       # ✅ added
                    "Surface": batch.get("surface"), # ✅ added
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

# =========================
# SCREEN 1: DASHBOARD (LOGO + HEADING)
# =========================
if st.session_state.page == "dashboard":

    cols = st.columns([1, 6])
    with cols[0]:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=90)
    with cols[1]:
        st.markdown("## SIPL Sorting Defect Report")
        st.caption("Home — choose an area below")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📋 Open Defect Reports", use_container_width=True):
            st.session_state.page = "batch"

    with col2:
        if os.path.exists(CSV_PATH):
            with open(CSV_PATH, "rb") as f:
                st.download_button(
                    "📊 Download Defect History (CSV)",
                    f,
                    "defect_history.csv",
                    use_container_width=True
                )
        else:
            st.info("No defect history yet")

# =========================
# SCREEN 2: BATCH DATA (ONLY SIZE & SURFACE ADDED)
# =========================
elif st.session_state.page == "batch":
    st.subheader("Batch Data")

    st.session_state.batch["date"] = st.date_input("Production Date")
    st.session_state.batch["shift"] = st.selectbox("Shift", ["Day", "Night"])
    st.session_state.batch["operator"] = st.text_input("Operator")
    st.session_state.batch["item_code"] = st.text_input("Item / SAP Code")
    st.session_state.batch["batch_code"] = st.text_input("Batch / SAP Batch")

    # ✅ ONLY NEW FIELDS
    st.session_state.batch["size"] = st.text_input("Tile Size (e.g. 600×600)")
    st.session_state.batch["surface"] = st.selectbox(
        "Surface",
        ["Matt", "Polished", "Glossy", "Satin", "Other"]
    )

    if st.button("Confirm & Enter Defects"):
        st.session_state.page = "departments"

# =========================
# SCREEN 3: DEPARTMENTS
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

# =========================
# SCREEN 4: DEFECT ENTRY (UNCHANGED)
# =========================
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
                st.session_state.defects[dept][defect] = max(
                    0, st.session_state.defects[dept][defect] - 1
                )
            c2.markdown(st.session_state.defects[dept][defect])
            if c3.button("➕", key=f"p-{dept}-{defect}"):
                st.session_state.defects[dept][defect] += 1

# =========================
# SCREEN 5: SUMMARY
# =========================
elif st.session_state.page == "summary":
    st.subheader("Batch Summary")

    bad_tiles = st.number_input("Number of defected tiles", min_value=0)
    total_tiles = st.number_input("Total tiles in batch", min_value=1)

    if st.button("💾 Save") and not st.session_state.saved:
        save_to_csv(
            st.session_state.batch,
            st.session_state.defects,
            bad_tiles,
            total_tiles
        )
        st.session_state.saved = True

    if st.session_state.saved:
        st.success("✅ Data saved successfully")

        if st.button("🔙 Go to Dashboard"):
            st.session_state.page = "dashboard"
            st.session_state.saved = False
            st.session_state.batch = {}
            st.session_state.defects = {d: {k: 0 for k in DEFECTS[d]} for d in DEFECTS}
