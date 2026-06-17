import streamlit as st
import pandas as pd
from datetime import datetime
import os

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
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# =========================
# DEFECT MASTER
# =========================
DEFECTS = {
    "SH/SD": ["IRON PARTICALS", "BODY HOLE", "BODY DUST", "R&D (Low MOR)", "STAIN PROBLEM"],
    "Press": ["LAMINATION", "CONTAMINATION", "CENTER CRACK", "SIDE CRACK",
              "DIPRESSION", "DUST", "DEPRESSION", "MIS PATTERN",
              "WEDGING", "Grid Mark", "CHIPS PROBLEM", "SMALL SIZE", "BUMP"],
    "G/L": ["DUST", "BLACK DUST", "COLOUR DROP", "COLOUR SPOT", "GLAZE DROP",
            "DIMPLE", "FLOW CUT", "FACE HOLE", "DIGITAL LINING",
            "DIGITAL MIS PRINT", "GLAZE CRACK", "PIN HOLE"],
    "Kiln": ["DUST", "BEND", "SIDE CRACK", "OVER FIRED",
             "SURFACE CRACK", "IRON PARTICALS"],
    "Polishing": ["SCRATCHES", "CHAMFERING", "CORNER CHIPPING",
                  "SIDE CHIPPING", "WASH OUT", "MIS POLISH"],
    "General": ["SAMPLE", "BROKEN", "R AND D SAMPLE", "QA CHIPPING"]
}

CSV_PATH = "data/defect_entry_flat.csv"
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
# SAVE CSV (FIXED COLUMN ORDER ✅)
# =========================
def save_to_csv_flat(batch, flat_data, bad, total):
    rows = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for row in flat_data:
        if row["qty"] > 0:
            rows.append({
                "Timestamp": ts,
                "Date": batch.get("date"),
                "Shift": batch.get("shift"),
                "Operator": batch.get("operator"),
                "Item": batch.get("item_code"),
                "Batch": batch.get("batch_code"),
                "Size": batch.get("size"),
                "Surface": batch.get("surface"),
                "Department": row["dept"],
                "Defect": row["defect"],
                "Qty": row["qty"],
                "Defective Tiles": bad,
                "Total Tiles": total
            })

    if not rows:
        return

    df = pd.DataFrame(rows)
    os.makedirs("data", exist_ok=True)

    if os.path.exists(CSV_PATH):
        old = pd.read_csv(CSV_PATH)
        df = pd.concat([old, df], ignore_index=True)

    df.to_csv(CSV_PATH, index=False)
# =========================
# SCREEN 1: DASHBOARD
# =========================
if st.session_state.page == "dashboard":

    col_logo, col_title = st.columns([1, 7])
    with col_logo:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=90)
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
        
        if st.button("Open History", use_container_width=True):
           st.session_state.page = "history"
# =========================
# SCREEN 2: BATCH DATA
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
# =========================
# NEW SINGLE TABLE SCREEN ✅
# =========================
elif st.session_state.page == "departments":

    st.subheader("Defect Entry (All Departments)")

    # ✅ Initialize flat structure
    if "flat_defects" not in st.session_state:
        flat = []
        for dept, defects in DEFECTS.items():
            for d in defects:
                flat.append({
                    "dept": dept,
                    "defect": d,
                    "qty": 0
                })
        st.session_state.flat_defects = flat

    data = st.session_state.flat_defects

    # ✅ Table header
    col1, col2, col3, col4 = st.columns([1, 3, 4, 3])
    col1.markdown("**S.No.**")
    col2.markdown("**Department**")
    col3.markdown("**Defect**")
    col4.markdown("**Quantity**")

    st.divider()

    last_dept = None

    for i, row in enumerate(data):

        c1, c2, c3, c4 = st.columns([1, 3, 4, 3])

        c1.write(i + 1)

        # Show department only once per group
        dept_display = row["dept"] if row["dept"] != last_dept else ""
        c2.write(dept_display)
        last_dept = row["dept"]

        c3.write(row["defect"])

        # ➖ ➕ buttons
        b1, b2, b3 = c4.columns([1,1,1])

        if b1.button("➖", key=f"minus_{i}"):
            data[i]["qty"] = max(0, data[i]["qty"] - 1)

        b2.markdown(f"### {data[i]['qty']}")

        if b3.button("➕", key=f"plus_{i}"):
            data[i]["qty"] += 1

        # ✅ Add new defect after department ends
        next_dept = data[i+1]["dept"] if i < len(data)-1 else None

        if next_dept != row["dept"]:
            new_defect = st.text_input(
                f"Add defect in {row['dept']}",
                key=f"add_{row['dept']}_{i}"
            )

            if st.button(f"Add → {row['dept']}", key=f"btn_add_{i}"):
                if new_defect.strip():
                    data.insert(i+1, {
                        "dept": row["dept"],
                        "defect": new_defect.upper(),
                        "qty": 0
                    })

            st.divider()

    # ✅ Finish
    if st.button("Finish"):
        st.session_state.page = "summary"
# =========================
# SCREEN 5: SUMMARY (GO BACK ✅)
# =========================
elif st.session_state.page == "summary":
    st.subheader("Summary")

    bad = st.number_input("Defective Tiles", min_value=0)
    total = st.number_input("Total Tiles", min_value=1)

    if st.button("Save"):
        save_to_csv_flat(
            st.session_state.batch,
            st.session_state.flat_defects,
            bad,
            total
        )
        st.session_state.saved = True

    if st.session_state.saved:
        st.success("✅ Data saved successfully")

        if st.button("🔙 Go back to Dashboard"):
            st.session_state.page = "dashboard"
            st.session_state.saved = False
            st.session_state.batch = {}
            st.session_state.defects = {d: {k: 0 for k in DEFECTS[d]} for d in DEFECTS}
# =========================
# SCREEN 6: HISTORY ✅
# =========================
elif st.session_state.page == "history":

    st.subheader("Defect History")

    if not os.path.exists(CSV_PATH):
        st.warning("No data available")
    else:
        df = pd.read_csv(CSV_PATH)
        df["Date"] = df["Date"].astype(str)

        # ✅ Aggregate batch-level data
        summary = df.groupby(
            ["Date", "Shift", "Operator", "Item", "Batch", "Size", "Surface"],
            as_index=False
        ).agg({
            "Defective Tiles": "max",
            "Total Tiles": "max"
        })

        # ✅ Defect %
        summary["Defect %"] = (
            summary["Defective Tiles"] / summary["Total Tiles"] * 100
        ).round(2)
        
        selected_index = st.selectbox(
            "Select Record to View Details",
            summary.index
        )
        if st.button("View Details"):
            st.session_state.selected_record = summary.loc[selected_index].to_dict()
            st.session_state.page = "detail"

        st.dataframe(summary, use_container_width=True)

        
        # ✅ Batch Details
        selected_row = summary.loc[selected_index].to_dict()
        # ✅ Batch Details
        st.subheader("Batch Details")
        col1, col2, col3 = st.columns(3)
        col1.write("Date:", st.session_state.batch.get("date", ""))
        col2.write("Shift:", st.session_state.batch.get("shift", ""))
        col3.write("Operator:", st.session_state.batch.get("operator", ""))

        col1, col2, col3 = st.columns(3)
        col1.write("Item:", st.session_state.batch.get("item_code", ""))
        col2.write("Batch:", st.session_state.batch.get("batch_code", ""))
        col3.write("Size:", st.session_state.batch.get("size", ""))

        st.write("Surface:", st.session_state.batch.get("surface", ""))
       # ✅ Defect Details
        st.subheader("Defect Details")

        filtered_df = df[
            (df["Date"] == str(selected_row["Date"])) &
            (df["Batch"] == str(selected_row["Batch"])) &
            (df["Item"] == str(selected_row["Item"]))
        ]
        if filtered_df.empty:
            st.warning("No matching defect data found")
        else:
            st.dataframe(
                filtered_df[["Department", "Defect", "Qty"]],
                use_container_width=True
            )






        # ✅ Download button at top
        csv = summary.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇ Download Report",
            csv,
            "defect_summary.csv",
            "text/csv",
            use_container_width=True
        )

    if st.button("⬅ Back"):
        st.session_state.page = "dashboard"
# =========================
# SCREEN 7: DETAIL PAGE ✅
# =========================
elif st.session_state.page == "detail":

    st.subheader("Detailed Defect Report")

    if "selected_record" not in st.session_state:
        st.warning("No record selected")
        if st.button("⬅ Back"):
            st.session_state.page = "history"
        st.stop()

    record = st.session_state.selected_record

    # ✅ Show Batch Details
    st.markdown("### Batch Details")

    col1, col2, col3 = st.columns(3)
    col1.write("Date:", record["Date"])
    col2.write("Shift:", record["Shift"])
    col3.write("Operator:", record["Operator"])

    col1, col2, col3 = st.columns(3)
    col1.write("Item:", record["Item"])
    col2.write("Batch:", record["Batch"])
    col3.write("Size:", record["Size"])

    st.write("Surface:", record["Surface"])

    st.divider()

    # ✅ Load full dataset
    df = pd.read_csv(CSV_PATH)

    # ✅ Filter for selected batch
    filtered_df = df[
        (df["Date"] == str(record["Date"])) &
        (df["Batch"] == str(record["Batch"])) &
        (df["Item"] == str(record["Item"]))
    ]

    if filtered_df.empty:
        st.warning("No defect data found")
    else:

        st.markdown("### Defect Details")

        # ✅ Group display like entry format
        last_dept = None

        col1, col2, col3, col4 = st.columns([1, 3, 4, 3])
        col1.markdown("**S.No.**")
        col2.markdown("**Department**")
        col3.markdown("**Defect**")
        col4.markdown("**Quantity**")

        st.divider()

        for i, row in filtered_df.iterrows():

            c1, c2, c3, c4 = st.columns([1, 3, 4, 3])

            c1.write(i + 1)

            dept_display = row["Department"] if row["Department"] != last_dept else ""
            c2.write(dept_display)
            last_dept = row["Department"]

            c3.write(row["Defect"])
            c4.write(row["Qty"])

    st.divider()

    if st.button("⬅ Back to History"):
        st.session_state.page = "history"

