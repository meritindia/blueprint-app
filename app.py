import streamlit as st
import pandas as pd
from io import BytesIO
import base64

st.set_page_config(page_title="Assessment Blueprint Generator", layout="wide")

# Title and Logo
col1, col2 = st.columns([1, 10])
with col1:
    st.image("logo.jpg", width=80)
with col2:
    st.title("Blueprint Generator - MERIT India")

st.markdown("""
This app helps you build a subject-wise assessment blueprint. Define section-wise weightage, cognitive domain splits, and manually enter distribution.
""")

# Step 1: Total Marks
st.subheader("Step 1: Total Marks for Theory Paper")
total_marks = st.number_input("Enter Total Marks", value=100)

# Step 2: Section-wise Distribution (%)
st.subheader("Step 2: Section-wise Distribution (%)")
col1, col2, col3 = st.columns(3)
with col1:
    mcq_pct = st.number_input("MCQ %", value=30)
with col2:
    saq_pct = st.number_input("SAQ %", value=30)
with col3:
    laq_pct = st.number_input("LAQ %", value=40)

mcq_marks = round(mcq_pct * total_marks / 100)
saq_marks = round(saq_pct * total_marks / 100)
laq_marks = round(laq_pct * total_marks / 100)

section_df = pd.DataFrame({
    "Section": ["MCQ", "SAQ", "LAQ"],
    "% Weightage": [mcq_pct, saq_pct, laq_pct],
    "Marks Allocated": [mcq_marks, saq_marks, laq_marks]
})
st.dataframe(section_df, use_container_width=True)

# Step 3: Cognitive Domain Distribution (%)
st.subheader("Step 3: Cognitive Domain Distribution (%) for Each Question Type")

cd_perc = {}
cd_marks = {}

for sec, sec_marks in zip(["MCQ", "SAQ", "LAQ"], [mcq_marks, saq_marks, laq_marks]):
    st.markdown(f"**{sec} Distribution**")
    col1, col2, col3 = st.columns(3)
    with col1:
        r = st.number_input(f"Recall % in {sec}", value=30, key=f"r_{sec}")
    with col2:
        u = st.number_input(f"Understand % in {sec}", value=30, key=f"u_{sec}")
    with col3:
        a = st.number_input(f"Apply % in {sec}", value=40, key=f"a_{sec}")
    cd_perc[sec] = [r, u, a]
    cd_marks[sec] = [round(r * sec_marks / 100), round(u * sec_marks / 100), round(a * sec_marks / 100)]

cdm_df = pd.DataFrame(cd_marks, index=["Recall", "Understand", "Apply"])
st.subheader("Step 4: Cognitive Domain Marks (Auto-calculated)")
st.dataframe(cdm_df, use_container_width=True)

# Step 5: Unit Data Input
st.subheader("Step 5: Enter Units and I x F Scores")
unit_data = st.text_area("Paste unit data (e.g., Unit Name, I x F Score)",
"""Gastrointestinal and Hepatobiliary, 143
Renal and Genitourinary, 101
Endocrine Disorders, 83
Rheumatology and Connective Tissue, 34""")

unit_rows = [row.strip().split(',') for row in unit_data.strip().split('\n') if row.strip() and len(row.strip().split(',')) == 2]
unit_df = pd.DataFrame(unit_rows, columns=["Unit", "IxF"])
unit_df["IxF"] = unit_df["IxF"].astype(float)
unit_df["Weightage %"] = round((unit_df["IxF"] / unit_df["IxF"].sum()) * 100)
unit_df["Marks"] = round((unit_df["Weightage %"] / 100) * total_marks)

# Step 6: Faculty Grid Entry
st.subheader("Step 6: Manual Grid Entry")
grid_template = pd.DataFrame(index=unit_df["Unit"], columns=[
    "MCQ-R", "MCQ-U", "MCQ-A",
    "SAQ-R", "SAQ-U", "SAQ-A",
    "LAQ-R", "LAQ-U", "LAQ-A"
])
grid_template.fillna(0, inplace=True)
edited_grid = st.data_editor(grid_template.astype(int), use_container_width=True, key="grid_editor")

# Calculations
total_row = edited_grid.sum().to_frame().T
unit_totals = edited_grid.sum(axis=1)
blueprint_df = pd.concat([unit_df, edited_grid], axis=1)
blueprint_df["Grid Total"] = unit_totals.values

# Display Final Table
st.subheader("Generated Blueprint Table")
styled_df = pd.concat([blueprint_df, total_row.rename(index={0: "Total"})])

# Fix: Format only numeric columns
formatted_df = styled_df.style.format({col: "{:.0f}" for col in styled_df.select_dtypes(include=['number']).columns})
st.dataframe(formatted_df, use_container_width=True)

# CSV Download
def convert_df_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv_data = convert_df_csv(blueprint_df)
st.download_button("📥 Download as CSV", csv_data, "blueprint_grid.csv", "text/csv")

# Footer
st.markdown("---")
st.markdown("Made by **MERIT India** | Logo © All rights reserved")
