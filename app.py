import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="SIPL Sorting Defect Report", layout="wide")

# =========================
# GLOBAL CSS
# =========================
st.markdown("""
<style>
.stApp {
    background-color: #FFE5D4;
}

/* force all text black */
* {
    color: black !important;
}

/* inputs */
input, textarea, select {
    background-color: white !important;
}

/* dashboard cards */
.dashboard-card {
    background: white;
    border-radius: 18px;
    padding: 40px;
    height: 240px;
    text-align: center;
    border: 2px solid #d6d6d6;
    box-shadow: 0 4px 10px rgba(0,0,0,0.12);
}

/* defect cards */
.defect-card {
    background: white;
    border: 2px solid #d6d6d6;
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# =========================
# LOAD LOGO
# =========================
def load_logo():
    if os.path.exists("logo.png"):
        return "logo.png"
    return None

LOGO_PATH = load_logo()

# =========================
# DEFECT MASTER
# =========================
DEFECTS = {
    "SH/SD": ["IRON PARTICALS", "BODY HOLE", "BODY DUST", "R&D (Low MOR)", "STAIN PROBLEM"],
    "Press": ["LAMINATION", "CONTAMINATION", "CENTER CRACK", "SIDE CRACK", "DIPRESSION",
              "DUST", "DEPRESSION", "MIS PATTERN", "WEDGING", "Grid Mark",
              "CHIPS PROBLEM", "SMALL SIZE", "BUMP"],
    "G/L": ["DUST", "BLACK DUST", "COLOUR DROP", "COLOUR SPOT", "GLAZE DROP",
            "DIMPLE", "FLOW CUT", "FACE HOLE", "DIGITAL LINING", "DIGITAL MIS PRINT",
            "GLAZE CRACK", "PIN HOLE", "T.R PROBLEM", "WATER DROP", "WHITE SPOT",
            "CONTAMINATION", "APPLICATION PROBLEM", "GLAZE STICKING",
            "HEAD MARK", "BUBBLES"],
    "Kiln": ["DUST", "BEND", "SIDE CRACK", "OVER FIRED",
             "SURFACE CRACK", "IRON PARTICALS"],
    "Polishing": ["SCRATCHES", "CHAMFERING", "CORNER CHIPPING",
                  "SIDE CHIPPING", "WASH OUT", "MIS POLISH"],
    "General": ["SAMPLE", "BROKEN", "R AND D SAMPLE", "QA CHIPPING"]
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

# =========================
# SAVE CSV
# =========================
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

    if rows:
        os.makedirs("data", exist_ok=True)
        pd.DataFrame(rows).to_csv(
            CSV_PATH, mode="a",
            header=not os.path.exists(CSV_PATH),
            index=False
        )

# =========================
# SCREEN 1: DASHBOARD (BIG SQUARES ✅)
# =========================
if st.session_state.page == "dashboard":

    col_logo, col_title = st.columns([1, 7])
    with col_logo:
        if LOGO_PATH:
            st.image(LOGO_PATH, width=90)
    with col_title:
        st.markdown("## SIPL Sorting Defect Report")
        st.caption("Select an option to continue")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="dashboard-card">
            <div style="font-size:60px;">📋</div>
            <h3>New Defect Entry</h3>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Defect Entry", use_container_width=True):
            st.session_state.page = "batch"

    with col2:
        st.markdown("""
        <div class="dashboard-card">
            <div style="font-size:60px;">📊</div>
            <h3>Download History</h3>
        </div>
        """, unsafe_allow_html=True)
        if os.path.exists(CSV_PATH):
            with open(CSV_PATH, "rb") as f:
                st.download_button(
                    "Download CSV",
                    f,
                    "defect_history.csv",
                    use_container_width=True
                )

# =========================
# SCREEN 2
# =========================
elif st.session_state.page == "batch":
    st.subheader("Batch Data")
    st.session_state.batch["date"] = st.date_input("Production Date")
    st.session_state.batch["shift"] = st.selectbox("Shift", ["Day", "Night"])
    st.session_state.batch["operator"] = st.text_input("Operator")
    st.session_state.batch["item_code"] = st.text_input("Item / SAP Code")
    st.session_state.batch["batch_code"] = st.text_input("Batch Code")
    st.session_state.batch["size"] = st.text_input("Tile Size")
    st.session_state.batch["surface"] = st.selectbox("Surface", ["Matt", "Polished", "Glossy", "Satin"])

    if st.button("Continue"):
        st.session_state.page = "departments"

# =========================
# SCREEN 3
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
# SCREEN 4: DEFECT ENTRY (BORDERED ✅)
# =========================
elif st.session_state.page == "defect_entry":
    dept = st.session_state.current_dept
    st.subheader(f"{dept} Defects")

    st.columns(1)

    cols = st.columns(3)
    for i, defect in enumerate(DEFECTS[dept]):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="defect-card">
                <b>{defect}</b>
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns([1, 1, 1])

            if c1.button("➖", key=f"m_{dept}_{defect}"):
                st.session_state.defects[dept][defect] = max(
                    0, st.session_state.defects[dept][defect] - 1
                )
            c2.markdown(f"### {st.session_state.defects[dept][defect]}")
            if c3.button("➕", key=f"p_{dept}_{defect}"):
                st.session_state.defects[dept][defect] += 1

    if st.button("⬅ Back"):
        st.session_state.page = "departments"

# =========================
# SCREEN 5
# =========================
elif st.session_state.page == "summary":
    st.subheader("Summary")
    bad = st.number_input("Defective Tiles", min_value=0)
    total = st.number_input("Total Tiles", min_value=1)

    if st.button("Save"):
        save_to_csv(st.session_state.batch, st.session_state.defects, bad, total)
        st.success("✅ Saved successfully")
        st.session_state.page = "dashboard"
        st.session_state.batch = {}
        st.session_state.defects = {d: {k: 0 for k in DEFECTS[d]} for d in DEFECTS}
