import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO
import base64

st.set_page_config(page_title="Blueprint Generator - MERIT India", layout="wide")

# ---------- Header Section ----------
col1, col2 = st.columns([1, 10])
with col1:
    st.image("logo.jpg", width=90)
with col2:
    st.markdown("""
        <h1 style='font-size:36px;'>Blueprint Generator – MERIT India</h1>
        <h5 style='color:gray;'>A tool to systematically design assessments in alignment with medical education objectives.</h5>
    """, unsafe_allow_html=True)

st.markdown("""
    <style>
    div[data-testid=stDataFrame] td {
        font-size: 16px;
    }
    .block-container {
        padding-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- Step 1: Total Marks ----------
st.markdown("### \U0001F522 Step 1: Total Marks for Theory Paper")
total_marks = st.number_input("Enter Total Marks", min_value=1, value=100)

# ---------- Step 2: Section-wise Distribution ----------
st.markdown("### \U0001F4C4 Step 2: Section-wise Distribution (%)")
section_input = st.text_area("Paste section data (e.g., MCQ, 30)", value="MCQ, 30\nSAQ, 30\nLAQ, 40")

try:
    section_lines = [line for line in section_input.splitlines() if line.strip() != ""]
    section_data = [line.split(',') for line in section_lines]
    section_df = pd.DataFrame(section_data, columns=["Section", "% Weightage"])
    section_df["% Weightage"] = pd.to_numeric(section_df["% Weightage"], errors='coerce')
    section_df["Marks Allocated"] = (section_df["% Weightage"] * total_marks / 100).round(0).astype(int)
    st.dataframe(section_df, use_container_width=True)
except:
    st.warning("Please enter valid section-wise distribution data.")

# ---------- Step 3: Cognitive Domain Distribution ----------
st.markdown("### \U0001F4D0 Step 3: Cognitive Domain Distribution (%) for Each Question Type")
cognitive_input = st.text_area("Paste cognitive distribution data (e.g., Recall in MCQ, 30)", 
    value="""Recall in MCQ, 30\nUnderstand in MCQ, 30\nApply in MCQ, 40\nRecall in SAQ, 30\nUnderstand in SAQ, 30\nApply in SAQ, 40\nRecall in LAQ, 30\nUnderstand in LAQ, 30\nApply in LAQ, 40""")

try:
    cog_lines = [line for line in cognitive_input.splitlines() if line.strip() != ""]
    cog_data = [line.split(',') for line in cog_lines]
    cog_df = pd.DataFrame(cog_data, columns=["Domain", "% Weight"])
    cog_df["% Weight"] = pd.to_numeric(cog_df["% Weight"], errors='coerce')
    st.dataframe(cog_df, use_container_width=True)
except:
    st.warning("Please enter valid cognitive domain distribution data.")

# ---------- Step 4: Derived Cognitive Table ----------
st.markdown("### \U0001F4CA Step 4: Derived Cognitive Matrix")
try:
    cog_matrix = pd.DataFrame(index=['Recall', 'Understand', 'Apply'], columns=['MCQ', 'SAQ', 'LAQ'])
    for _, row in cog_df.iterrows():
        for level in cog_matrix.index:
            if level in row["Domain"]:
                for sec in cog_matrix.columns:
                    if sec in row["Domain"]:
                        cog_matrix.loc[level, sec] = row["% Weight"]
    cog_matrix = cog_matrix.fillna(0).astype(int)
    st.dataframe(cog_matrix, use_container_width=True)
except:
    st.warning("Cognitive Matrix generation failed.")

# ---------- Step 5: Enter Units and IxF ----------
st.markdown("### \U0001F5C3️ Step 5: Enter Units and Ix F Scores")
st.caption("Paste unit data (e.g., Unit Name, I x F Score)")
unit_input = st.text_area("Paste Units", value="""Gastrointestinal and Hepatobiliary, 143\nRenal and Genitourinary, 101\nEndocrine Disorders, 83\nRheumatology and Connective Tissue, 34""")

unit_lines = [line for line in unit_input.splitlines() if line.strip() != ""]
unit_data = [line.split(',') for line in unit_lines if ',' in line]
unit_df = pd.DataFrame(unit_data, columns=["Unit", "IxF"])
unit_df["IxF"] = pd.to_numeric(unit_df["IxF"], errors='coerce')
unit_df = unit_df.dropna()
unit_df["IxF"] = unit_df["IxF"].astype(int)
total_ixf = unit_df["IxF"].sum()
unit_df["Weightage %"] = ((unit_df["IxF"] / total_ixf) * 100).round(0)
unit_df["Marks"] = ((unit_df["Weightage %"] * total_marks) / 100).round(0).astype(int)

# ---------- Step 6: Manual Grid Entry ----------
st.markdown("### \U0001F4CB Step 6: Manual Grid Entry")
grid_columns = ["MCQ-R", "MCQ-U", "MCQ-A", "SAQ-R", "SAQ-U", "SAQ-A", "LAQ-R", "LAQ-U", "LAQ-A"]
grid_template = pd.DataFrame(0, index=unit_df["Unit"], columns=grid_columns)
styled_grid = st.data_editor(grid_template.copy(), use_container_width=True, num_rows="dynamic")

# ---------- Step 7: Final Blueprint Generation ----------
st.markdown("### \U0001F4D1 Generated Blueprint Table")
unit_totals = styled_grid.sum(axis=1)
final_df = pd.concat([unit_df.set_index("Unit"), styled_grid], axis=1)
final_df["Grid Total"] = unit_totals
st.dataframe(final_df.reset_index(), use_container_width=True)

# ---------- Step 8: CSV Export ----------
st.download_button(
    label="\U0001F4BE Download as CSV",
    data=final_df.reset_index().to_csv(index=False).encode('utf-8'),
    file_name="blueprint_grid.csv",
    mime='text/csv'
)

# ---------- Step 9: Footer ----------
st.markdown("""
    ---
    <div style='font-size:14px; color: gray;'>
        © 2025 MERIT India. All rights reserved. | For support: <a href='mailto:support@meritindia.org'>support@meritindia.org</a>
    </div>
""", unsafe_allow_html=True)
